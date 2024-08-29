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

from odoo import api, models
from collections import defaultdict
from datetime import datetime, timedelta


class AttendanceReportPdf(models.AbstractModel):
    _name = 'report.aspl_hr_attendance_report.attendance_report_pdf'
    _description = 'Generates attendance report for employees based on Employee or Department'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('aspl_hr_attendance_report.attendance_report_pdf')
        return {
            'doc_ids': self.env['attendance.report.wizard'].browse(docids[0]),
            'doc_model': report.model,
            'docs': self,
            'employee_data': self.employee_data,
        }

    def employee_data(self, obj):
        if obj.report_by == 'employee':
            if not obj.employee_ids:
                emp_ids = self.env['hr.employee'].search([]).ids
                domain = '''he.id in %s''' % (str(tuple(emp_ids)))
            else:
                emp_ids = obj.employee_ids.ids
                domain = '''he.id in (%s)''' % (','.join(map(str, emp_ids)))
        else:
            if not obj.department_ids:
                dept_ids = self.env['hr.department'].search([]).ids
                emp_ids = self.env['hr.employee'].search([('department_id', 'in', dept_ids)]).ids
                domain = '''he.id in %s''' % (str(tuple(emp_ids)))
            else:
                dept_ids = obj.department_ids.ids
                emp_ids = self.env['hr.employee'].search([('department_id', 'in', dept_ids)]).ids
                domain = '''he.id in (%s)''' % (','.join(map(str, emp_ids)))

        start_date = datetime.strptime(str(obj.start_date), '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
        end_date = datetime.strptime(str(obj.end_date), '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')
        first_query = '''
                   SELECT he.id as employee_id , he.name as employee_name, ha.id attendance_id,
                   count(ha.check_in) as count_check_in,  count(ha.check_out) as count_check_out,
                   ha.check_in at time zone 'utc' as check_in_date, ha.check_out at time zone 'utc' as check_out_date,
                   hd.id as department_id, hd.name as department_name
                   FROM hr_attendance ha
                   LEFT JOIN hr_employee he ON he.id = ha.employee_id
                   LEFT JOIN hr_department hd ON hd.id = he.department_id
                   WHERE ''' + (str(domain)) + ''' AND
                   ha.check_in >= '%s' at time zone 'utc'
                   AND ha.check_out <= '%s' at time zone 'utc' AND ha.check_out is not null
                   GROUP BY he.id, ha.id,ha.check_in, ha.check_out, he.name, hd.id,hd.name
               ''' % (start_date, end_date)
        self._cr.execute(first_query)
        attendance_detail = self._cr.dictfetchall()
        attendance_dict = {}
        late_count_dict = {}
        att_lst = []
        late_hour_dict = {}
        late_days_dict = {}
        for each_attendance in attendance_detail:
            employee_id = self.env['hr.employee'].sudo().browse(each_attendance.get('employee_id'))
            day_week = each_attendance.get('check_in_date').weekday()
            if employee_id.resource_calendar_id.attendance_ids.filtered(lambda l: l.dayofweek == str(day_week)):
                week_lst = employee_id.resource_calendar_id.attendance_ids.mapped('dayofweek')
                lst = []
                for each in week_lst:
                    if each not in lst:
                        lst.append(each)
                lst1 = ['0', '1', '2', '3', '4', '5', '6']
                set1 = list(set(lst1) - set(lst))
                day_week = each_attendance.get('check_in_date').weekday()
                work_date_lst = []
                for i in range(0, (datetime.strptime(str(obj.end_date), '%Y-%m-%d').date() - datetime.strptime(
                        str(obj.start_date), '%Y-%m-%d').date()).days + 1):
                    if str((datetime.strptime(str(obj.start_date), '%Y-%m-%d') + timedelta(
                            days=i)).date().weekday()) not in set1:
                        work_date_lst.append(
                            (datetime.strptime(str(obj.start_date), '%Y-%m-%d') + timedelta(days=i)).date())

                attendance_ids = self.env['hr.attendance'].search([('check_in', '>=', start_date),
                                                                   ('check_in', '<=', end_date),
                                                                   ('employee_id', '=', employee_id.id),
                                                                   ])
                check_in_date = attendance_ids.mapped('check_in')
                check_in_details = []
                for each in check_in_date:
                    if datetime.strptime(str(each), '%Y-%m-%d %H:%M:%S').date() not in check_in_details:
                        check_in_details.append(datetime.strptime(str(each), '%Y-%m-%d  %H:%M:%S').date())
                absent_employee = list(set(work_date_lst) - set(check_in_details))

                for each in \
                        employee_id.resource_calendar_id.attendance_ids.filtered(
                            lambda l: l.dayofweek == str(day_week))[0]:
                    minutes = each.hour_from * 60
                    hours, minutes = divmod(minutes, 60)
                    work_hour = "%02d:%02d" % (hours, minutes) + ':00'
                    minute_list = work_hour.split(':')
                    weekday_date = each_attendance.get('check_in_date').replace(minute=int(minute_list[1]),
                                                                                hour=int(minute_list[0]), second=00)
                    if each_attendance.get('check_in_date') > weekday_date:
                        if each_attendance.get('employee_id') not in late_count_dict:
                            emp_attendance_ids = self.env['hr.attendance'].search(
                                [('employee_id', '=', each_attendance.get('employee_id'))])
                            emp_attendance_id = min(emp_attendance_ids.filtered(
                                lambda x: datetime.strptime(str(x.check_in),
                                                            '%Y-%m-%d %H:%M:%S').date() == each_attendance.get(
                                    'check_in_date').date()).ids)
                            if emp_attendance_id not in att_lst and emp_attendance_id == each_attendance.get(
                                    'attendance_id'):
                                diff = each_attendance.get('check_in_date') - weekday_date
                                each_attendance.update({'diff': diff.seconds / 60})
                                late_count_dict[each_attendance.get('employee_id')] = [each_attendance]
                                if each_attendance.get('employee_id') in late_days_dict:
                                    late_days_dict[each_attendance.get('employee_id')] += 1
                                else:
                                    late_days_dict[each_attendance.get('employee_id')] = 1
                                if each_attendance.get('employee_id') in late_hour_dict:
                                    late_hour_dict[each_attendance.get('employee_id')] += diff.seconds / 60
                                else:
                                    late_hour_dict[each_attendance.get('employee_id')] = diff.seconds / 60
                                att_lst.append(emp_attendance_id)
                        else:
                            emp_attendance_ids = self.env['hr.attendance'].search(
                                [('employee_id', '=', each_attendance.get('employee_id'))])
                            emp_attendance_id = min(emp_attendance_ids.filtered(
                                lambda x: datetime.strptime(str(x.check_in),
                                                            '%Y-%m-%d %H:%M:%S').date() == each_attendance.get(
                                    'check_in_date').date()).ids)
                            if emp_attendance_id not in att_lst:
                                diff = each_attendance.get('check_in_date') - weekday_date
                                each_attendance.update({'diff': diff.seconds / 60})
                                late_count_dict[each_attendance.get('employee_id')].append(each_attendance)
                                if each_attendance.get('employee_id') in late_days_dict:
                                    late_days_dict[each_attendance.get('employee_id')] += 1
                                else:
                                    late_days_dict[each_attendance.get('employee_id')] = 1
                                if each_attendance.get('employee_id') in late_hour_dict:
                                    late_hour_dict[each_attendance.get('employee_id')] += diff.seconds / 60
                                else:
                                    late_hour_dict[each_attendance.get('employee_id')] = diff.seconds / 60
                                att_lst.append(emp_attendance_id)

                if not each_attendance.get('employee_id') in attendance_dict:
                    each_attendance['work_day_count'] = len(work_date_lst)
                    each_attendance['absent_count'] = len(absent_employee) if len(absent_employee) else 0
                    attendance_dict[each_attendance.get('employee_id')] = [each_attendance]
                else:
                    get_count_check_in = each_attendance.get('count_check_in')
                    get_count_check_out = each_attendance.get('count_check_out')

                    for each in attendance_dict[each_attendance.get('employee_id')]:
                        each['count_check_in'] = each.get('count_check_in') + get_count_check_in
                        each['count_check_out'] = each.get('count_check_out') + get_count_check_out
                        each['work_day_count'] = len(work_date_lst)
                        each['absent_count'] = len(absent_employee) if len(absent_employee) else 0
        for each in attendance_dict.values():
            for each_item in each:
                if each_item.get('employee_id'):
                    each_item['late_count'] = late_days_dict.get(each_item.get('employee_id')) or 0
                if each_item.get('employee_id'):
                    each_item['diff'] = late_hour_dict.get(each_item.get('employee_id')) or 0.0
        if obj.report_by == 'department':
            department_dict = defaultdict(list)
            for each in attendance_dict:
                employee_lst = attendance_dict[each]
                if len(employee_lst) > 0:
                    department_id = employee_lst[0].get('department_id')
                    if department_id:
                        department_dict[department_id].extend(attendance_dict[each])
            return department_dict
        return attendance_dict

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
