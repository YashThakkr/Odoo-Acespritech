# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
import pytz
from odoo.exceptions import ValidationError, UserError


class HrEmployeeOvertime(models.Model):
    _name = "hr.employee.overtime"
    _inherit = 'mail.thread'
    _description = 'HR Employee Overtime'
    _order = 'id desc'

    @api.depends('line_ids.overtime', 'line_ids.overtime_approved')
    def _compute_overtime(self):
        for overtime in self:
            total_overtime = total_approved_overtime = 0.0
            for line in overtime.line_ids:
                total_overtime += line.overtime
                total_approved_overtime += line.overtime_approved
            overtime.update({
                'total_overtime': total_overtime,
                'total_approved_overtime': total_approved_overtime,
            })

    def _default_employee(self):
        return self.env.user.employee_id

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        if not self.env.user.has_group('base.group_system'):
            args += [('employee_id.user_id', '=', self.env.user.id)]
        res = super(HrEmployeeOvertime, self).search(args, offset=offset, limit=limit, order=order)
        return res

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
                                  ondelete='cascade', readonly=1)
    name = fields.Char(string="Name")
    date = fields.Date(string="Date", default=date.today(), readonly=1)
    based_on = fields.Selection([('weekday', 'Weekday'),
                                 ('weekend', 'Weekend'), ('holiday', 'Holiday')], 'Based On')
    state = fields.Selection([('draft', 'Draft'),
                              ('to_be_approved', 'To Be Approved'),
                              ('approved', 'Approved'),
                              ('paid', 'Paid'),
                              ('cancelled', 'Cancelled')], default='draft',
                             string="State", tracking=True)
    ot_rate = fields.Float(string='OT Rate')
    overtime = fields.Float(string="Overtime")
    payslip_id = fields.Many2one('hr.payslip', string="Related Payslip")
    line_ids = fields.One2many('overtime.line', 'overtime_id', string="Overtime ")
    total_overtime = fields.Float('Total Overtime', compute="_compute_overtime")
    total_approved_overtime = fields.Float('Total Approved Overtime', compute="_compute_overtime")

    def action_overtime_calculate(self, res):
        data_dic_overtime = {}
        hours = 0.0
        message = ""
        date = ""
        if self.env.user.has_group('aspl_hr_overtime_ee.group_overtime_manual_overtime'):
            if res.line_ids:
                for active_line in res.line_ids:
                    line_ids = self.env['overtime.line'].search(
                        [('date', '=', active_line.date), ('employee_id', '=', active_line.employee_id.id)])
                    for line in line_ids:
                        if line.based_on == 'weekday' and line.date == active_line.date:
                            if line.date not in data_dic_overtime:
                                working_hour = line.employee_id.resource_calendar_id
                                overtime_day = line.date.weekday()
                                for calendar_attendance in working_hour.attendance_ids:
                                    if int(overtime_day) == int(calendar_attendance.dayofweek):
                                        hours += calendar_attendance.hour_to - calendar_attendance.hour_from
                                data_dic_overtime[line.date] = {'amount': line.overtime, }
                                message = line.based_on
                                date = line.date
                            else:
                                data_dic_overtime[line.date]['amount'] += line.overtime
                        elif line.date == active_line.date:
                            if line.date not in data_dic_overtime:
                                hours = 0.0
                                data_dic_overtime[line.date] = {'amount': line.overtime, }
                            else:
                                hours = 0.0
                                data_dic_overtime[line.date]['amount'] += line.overtime
                            message = line.based_on
                            date = line.date
                        total_overtime = 0.0
                        for date, amount_dict in data_dic_overtime.items():
                            for amount_key, amount_val in amount_dict.items():
                                total_overtime = amount_val
                        total_overtime += hours
                        if (total_overtime) > 12:
                            if message == 'weekday':
                                raise UserError(_('you can  not apply more than 4 hours on date %s as its a %s') % (date, message))
                            else:
                                raise UserError(_('you can  not apply more than 12 hours on date %s as its a %s') % (date, message))

    @api.model_create_multi
    def create(self, vals_list):
        ot_name = self.env['ir.sequence'].next_by_code('hr.employee.overtime')
        for vals in vals_list:
            if ot_name:
                vals.update({'name': ot_name})
        res = super(HrEmployeeOvertime, self).create(vals)
        self.action_overtime_calculate(res)
        return res

    def write(self, vals):
        res = super(HrEmployeeOvertime, self).write(vals)
        self.action_overtime_calculate(self)
        return res

    def get_date(self, date_time):
        if self._context.get('tz', False):
            tz = pytz.timezone(self._context.get('tz'))
        elif self.env.user.tz:
            tz = pytz.timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if sign == '-':
            date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=hour_tz, minutes=min_tz)
        if sign == '+':
            date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=hour_tz, minutes=min_tz)
        return date

    @api.model
    def generate_employee_overtime(self):
        config_id = self.env['ir.config_parameter'].search([], limit=1, order="id desc")
        config_id = self.env['ir.config_parameter'].sudo().get_param
        weekday_ot_rate = float(config_id('aspl_hr_overtime_ee.weekday_ot_rate'))
        holiday_ot_rate = float(config_id('aspl_hr_overtime_ee.weekend_ot_rate'))
        weekend_ot_rate = float(config_id('aspl_hr_overtime_ee.holiday_ot_rate'))
        ot_time_difference_limit = int(config_id('aspl_hr_overtime_ee.ot_time_difference_limit'))
        manually_create_overtime_req = config_id('aspl_hr_overtime_ee.manually_create_overtime_req')
        payslip_date_range = config_id('aspl_hr_overtime_ee.payslip_date_range')
        for employee in self.env['hr.employee'].search([]):
            is_weekday = False
            is_holiday = False
            ot_rate = 0.0
            resource_calendar_id = employee.resource_calendar_id if employee.resource_calendar_id \
                else config_id

            if resource_calendar_id:

                res_calendar_attendance_id = False
                res_holidays_attendance_id = False
                for each_res_calendar_attendance in resource_calendar_id.attendance_ids:
                    if int(each_res_calendar_attendance.dayofweek) == date.today().weekday():
                        if not res_calendar_attendance_id or \
                                (res_calendar_attendance_id and res_calendar_attendance_id.hour_to <= each_res_calendar_attendance.hour_to):
                            res_calendar_attendance_id = each_res_calendar_attendance
                        is_weekday = True
                for each_res_holiday_attendance in resource_calendar_id.global_leave_ids:
                    date_from = each_res_holiday_attendance.date_from.strftime('%d/%m/%Y')
                    date_from = datetime.strptime(date_from, '%d/%m/%Y').date()
                    date_to = each_res_holiday_attendance.date_to.strftime('%d/%m/%Y')
                    date_to = datetime.strptime(date_to, '%d/%m/%Y').date()
                    delta = date_to - date_from
                    for i in range(delta.days + 1):
                        date_holiday = date_from + timedelta(days=i)
                        if date_holiday == date.today():
                            if not res_holidays_attendance_id or \
                                    (res_holidays_attendance_id and res_holidays_attendance_id.hour_to <= each_res_calendar_attendance.hour_to):
                                res_holidays_attendance_id = each_res_calendar_attendance
                            is_holiday = True
                if res_calendar_attendance_id:
                    ot_rate = employee.weekday_ot_rate if employee.weekday_ot_rate \
                        else weekday_ot_rate if (weekday_ot_rate) \
                        else 0.0
                elif res_holidays_attendance_id:
                    ot_rate = employee.holiday_ot_rate if employee.holiday_ot_rate \
                        else holiday_ot_rate if (holiday_ot_rate) \
                        else 0.0
                else:
                    ot_rate = employee.weekend_ot_rate if employee.weekend_ot_rate \
                        else weekend_ot_rate if (weekend_ot_rate) \
                        else 0.0
            if res_holidays_attendance_id:
                hour_to_hr = (str(res_holidays_attendance_id.hour_to).split(".")[0] if '.' in str(
                    res_holidays_attendance_id.hour_to) \
                                  else str(res_holidays_attendance_id.hour_to)) if res_holidays_attendance_id else '00'
                hour_to_minute = (
                    str(int(float(str(res_holidays_attendance_id.hour_to).split(".")[1]) * 0.6)) if '.' in str(
                        res_holidays_attendance_id.hour_to) \
                        else '00') if res_holidays_attendance_id else '00'
            else:
                hour_to_hr = (
                    str(res_calendar_attendance_id.hour_to).split(".")[0] if '.' in str(
                        res_calendar_attendance_id.hour_to) \
                        else str(res_calendar_attendance_id.hour_to)) if res_calendar_attendance_id else '00'
                hour_to_minute = (
                    str(int(float(str(res_calendar_attendance_id.hour_to).split(".")[1]) * 0.6)) if '.' in str(
                        res_calendar_attendance_id.hour_to) \
                        else '00') if res_calendar_attendance_id else '00'
            date_to_add = datetime.now().replace(hour=int(hour_to_hr), minute=int(hour_to_minute), second=0)
            ot_time_difference_limit = ot_time_difference_limit if ot_time_difference_limit else 0.0
            if ot_time_difference_limit:
                date_to_add = date_to_add + timedelta(minutes=ot_time_difference_limit)

            date_to_compare = self.get_date(str(date_to_add.strftime("%Y-%m-%d %H:%M:%S")))

            if is_holiday:
                attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                   ('check_out', '>=', str(date_to_compare)),
                                                                   ('check_out', '<=', str(self.get_date(
                                                                       str(date.today()) + " 23:59:59"))),
                                                                   ('employee_ot_id', '=', False)])
            elif is_weekday:
                attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                   ('check_out', '>=', str(date_to_compare)),
                                                                   ('check_out', '<=', str(self.get_date(
                                                                       str(date.today()) + " 23:59:59"))),
                                                                   ('employee_ot_id', '=', False)])
            else:
                attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                   ('check_out', '>=', str(self.get_date(
                                                                       str(date.today()) + " 00:00:00"))),
                                                                   ('check_out', '<=', str(self.get_date(
                                                                       str(date.today()) + " 23:59:59"))),
                                                                   ('employee_ot_id', '=', False)])
            overtime_min = 0.0
            overtime_hour = 0.0
            for each_attendance_id in attendance_ids:
                if is_holiday:
                    check_in_date = date_to_compare if date_to_compare > fields.Datetime.from_string(
                        each_attendance_id.check_in) \
                        else fields.Datetime.from_string(each_attendance_id.check_in)
                    based_on = 'holiday'
                elif is_weekday:
                    check_in_date = date_to_compare if date_to_compare > fields.Datetime.from_string(
                        each_attendance_id.check_in) \
                        else fields.Datetime.from_string(each_attendance_id.check_in)
                    based_on = 'weekday'
                else:
                    check_in_date = fields.Datetime.from_string(each_attendance_id.check_in)
                    based_on = 'weekend'
                check_out_date = fields.Datetime.from_string(each_attendance_id.check_out)
                duration = (check_out_date - check_in_date).total_seconds()
                overtime_min += divmod(duration, 60)[0]
                overtime_hour += (overtime_min / 60)
            if not self.env.user.has_group('aspl_hr_overtime_ee.group_overtime_manual_overtime'):
                if overtime_hour and ot_rate:
                    employee_ot_id = self.env['hr.employee.overtime'].create({'employee_id': employee.id,
                                                                              'date': date.today(),
                                                                              'state': 'to_be_approved',
                                                                              'line_ids': [(0, 0, {
                                                                                  'employee_id': employee.id,
                                                                                  'date': date.today(),
                                                                                  'based_on': based_on,
                                                                                  'ot_rate': ot_rate,
                                                                                  'overtime': overtime_hour,
                                                                                  'overtime_approved': overtime_hour,
                                                                                  'overtime_minute': overtime_min})]
                                                                              })
                    attendance_ids.update({'employee_ot_id': employee_ot_id.id})

    def emp_overtime_approve(self):
        self.ensure_one()
        self.state = 'approved'

    def emp_overtime_cancel(self):
        self.ensure_one()
        attendance_ids = self.env['hr.attendance'].search([('employee_ot_id', '=', self.id)])
        if attendance_ids:
            attendance_ids.update({'employee_ot_id': False})
        self.state = 'cancelled'

    def to_be_approve(self):
        self.ensure_one()
        self.state = 'to_be_approved'


class OvertimeLine(models.Model):
    _name = 'overtime.line'
    _description = 'Overtime Line'
    _order = 'id desc'

    def _default_employee(self):
        return self.env.user.employee_id

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
                                  ondelete='cascade', readonly=1)
    description = fields.Char('Description')
    date = fields.Date(string="Date")
    based_on = fields.Selection([('weekday', 'Weekday'),
                                 ('weekend', 'Weekend'), ('holiday', 'Holiday')], 'Based On')
    ot_rate = fields.Float(string='OT Rate')
    overtime = fields.Float(string="Overtime")
    overtime_minute = fields.Float(string="Overtime Minutes")
    overtime_approved = fields.Float(string="Approve Overtime")
    overtime_id = fields.Many2one('hr.employee.overtime', string='Over Time')
    payslip_id = fields.Many2one('hr.payslip', string="Related Payslip")
    state = fields.Selection([('draft', 'Draft'),
                              ('to_be_approved', 'To Be Approved'),
                              ('approved', 'Approved'),
                              ('paid', 'Paid'),
                              ('cancelled', 'Cancelled')], default='draft', string="State", related="overtime_id.state")

    @api.onchange('date')
    def _onchange_overtime_line(self):
        lst_date = []
        active_id = self.env.user
        config_id = self.env['ir.config_parameter'].search([], limit=1, order="id desc")
        config_id = self.env['ir.config_parameter'].sudo().get_param
        weekday_ot_rate = float(config_id('aspl_hr_overtime_ee.weekday_ot_rate'))
        holiday_ot_rate = float(config_id('aspl_hr_overtime_ee.weekend_ot_rate'))
        weekend_ot_rate = float(config_id('aspl_hr_overtime_ee.holiday_ot_rate'))
        ot_time_difference_limit = int(config_id('aspl_hr_overtime_ee.ot_time_difference_limit'))
        manually_create_overtime_req = config_id('aspl_hr_overtime_ee.manually_create_overtime_req')
        payslip_date_range = config_id('aspl_hr_overtime_ee.payslip_date_range')
        for line in self:
            if line.date:
                for employee in self.env['hr.employee'].search([('user_id', '=', active_id.id)]):
                    is_weekday = False
                    is_holiday = False
                    ot_rate = 0.0
                    resource_calendar_id = employee.resource_calendar_id if employee.resource_calendar_id \
                        else config_id
                    if resource_calendar_id:
                        res_calendar_attendance_id = False
                        res_holidays_attendance_id = False
                        for each_res_calendar_attendance in resource_calendar_id.attendance_ids:
                            if int(each_res_calendar_attendance.dayofweek) == line.date.weekday():
                                if not res_calendar_attendance_id or \
                                        (
                                                res_calendar_attendance_id and res_calendar_attendance_id.hour_to <= each_res_calendar_attendance.hour_to):
                                    res_calendar_attendance_id = each_res_calendar_attendance
                                is_weekday = True
                        for each_res_holiday_attendance in resource_calendar_id.global_leave_ids:
                            date_from = each_res_holiday_attendance.date_from.strftime('%d/%m/%Y')
                            date_from = datetime.strptime(date_from, '%d/%m/%Y').date()
                            date_to = each_res_holiday_attendance.date_to.strftime('%d/%m/%Y')
                            date_to = datetime.strptime(date_to, '%d/%m/%Y').date()
                            delta = date_to - date_from
                            for i in range(delta.days + 1):
                                date_holiday = date_from + timedelta(days=i)
                                if date_holiday == line.date:
                                    if not res_holidays_attendance_id or \
                                            (res_holidays_attendance_id and res_holidays_attendance_id.hour_to <= each_res_calendar_attendance.hour_to):
                                        res_holidays_attendance_id = each_res_calendar_attendance
                                    is_holiday = True

                        if res_calendar_attendance_id:
                            ot_rate = employee.weekday_ot_rate if employee.weekday_ot_rate \
                                else weekday_ot_rate if (weekday_ot_rate) \
                                else 0.0
                        elif res_holidays_attendance_id:
                            ot_rate = employee.holiday_ot_rate if employee.holiday_ot_rate \
                                else holiday_ot_rate if (holiday_ot_rate) \
                                else 0.0
                        else:
                            ot_rate = employee.weekend_ot_rate if employee.weekend_ot_rate \
                                else weekend_ot_rate if (weekend_ot_rate) \
                                else 0.0
                ot_time_difference_limit = ot_time_difference_limit if ot_time_difference_limit else 0.0
                if line.overtime:
                    overtime_minute = ((line.overtime * 60) - ot_time_difference_limit)
                else:
                    overtime_minute = 0
                if is_holiday:
                    line.update({'based_on': 'holiday', 'ot_rate': ot_rate, 'overtime_minute': overtime_minute})
                elif is_weekday:
                    line.update({'based_on': 'weekday', 'ot_rate': ot_rate, 'overtime_minute': overtime_minute})
                else:
                    line.update({'based_on': 'weekend', 'ot_rate': ot_rate, 'overtime_minute': overtime_minute})

    @api.onchange('overtime')
    def _onchange_hour(self):
        if self.overtime:
            self.overtime_approved = self.overtime

    @api.onchange('overtime_approved')
    def _overtime_approved_change(self):
        if self.overtime or self.overtime_approved:
            if self.overtime_approved > self.overtime:
                raise UserError(_('Approved overtime hours can not be more then overtime hours.. '))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
