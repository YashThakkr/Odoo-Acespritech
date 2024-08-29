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
import base64
import contextlib
from io import BytesIO
from typing import io

import xlwt
from odoo import fields, models, api, _


class AttendanceReportWizard(models.TransientModel):
    _name = 'attendance.report.wizard'
    _description = 'Attendance report wizard'

    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    report_by = fields.Selection([('employee', 'Employee'), ('department', 'Department')], required=True,
                                 string='Report by', default='employee')
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    department_ids = fields.Many2many('hr.department', string='Department')
    view_by = fields.Selection([('pdf', 'PDF'), ('excel', 'Excel')], string='View by', required=True, default='pdf')
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')

    file_data = fields.Binary(string='File')
    file_name = fields.Char(string='File Name', readonly=True)

    def print_report(self):
        '''Prints PDF Report for Employee Attendance'''
        if self.view_by == 'pdf':
            return self.env.ref('aspl_hr_attendance_report_ee.pdf_attendance_report').report_action(self)
        else:
            self.generate_xls_report()
            return {
                'name': 'HR Attendance Report',
                'res_model': self._name,
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'type': 'ir.actions.act_window',
            }

    def generate_xls_report(self):
        '''Prints XLS Report for EMployee Attendance'''
        self.ensure_one()
        employee_dict = self.env['report.aspl_hr_attendance_report_ee.attendance_report_pdf'].employee_data(
            self)
        workbook = xlwt.Workbook(encoding="utf-8")

        header_style = xlwt.XFStyle()
        fontP = xlwt.Font()
        fontP.bold = True

        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER

        header_style.font = fontP
        header_style.alignment = alignment

        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']
        header_style.pattern = pattern

        style_detail_1 = xlwt.easyxf('font: bold on,height 200;align: vertical center, horizontal center;')

        worksheet = workbook.add_sheet('HR Attendance Report')
        worksheet.write_merge(0, 2, 0, 6, 'Attendance Report', style=header_style)

        if self.report_by == 'employee':
            worksheet.col(0).width = 6000
            worksheet.col(5).width = 4500
            worksheet.col(6).width = 4500

            worksheet.write_merge(3, 3, 0, 6, '{} to {}'.format(self.start_date, self.end_date), style_detail_1)

            worksheet.write(4, 0, 'Name/Employee', xlwt.easyxf('font: bold on,height 200;align: horiz left;'))
            worksheet.write(4, 1, 'Work(Day)', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
            worksheet.write(4, 2, 'Late(Day)', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
            worksheet.write(4, 3, 'Late(min)', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
            worksheet.write(4, 4, 'Absent(Day)', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
            worksheet.write(4, 5, 'Total Checkin', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
            worksheet.write(4, 6, 'Total Checkout', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))

            row = 4

            for vals in employee_dict.values():
                row += 1
                worksheet.write(row, 0, vals[0]['employee_name'])
                worksheet.write(row, 1, vals[0]['work_day_count'])
                worksheet.write(row, 2, vals[0]['late_count'])
                worksheet.write(row, 3, '%.2f' % (vals[0]['diff']), xlwt.easyxf('align: horiz right;'))
                worksheet.write(row, 4, vals[0]['absent_count'])
                worksheet.write(row, 5, vals[0]['count_check_in'])
                worksheet.write(row, 6, vals[0]['count_check_out'])

        elif self.report_by == 'department':
            worksheet.col(0).width = 6000
            worksheet.col(5).width = 4500
            worksheet.col(6).width = 4500

            worksheet.write_merge(3, 3, 0, 6, '{} to {}'.format(self.start_date, self.end_date), style_detail_1)

            row = 3

            for vals in employee_dict.values():
                row += 2
                worksheet.write_merge(row, row, 0, 6, next(iter(vals[0]['department_name'].values())), xlwt.easyxf(
                    'font: bold on,height 200;align: vertical center;pattern: pattern solid, fore_colour gray25;'))
                row += 1
                worksheet.write(row, 0, 'Name/Employee', xlwt.easyxf('font: bold on,height 200;align: horiz left;'))
                worksheet.write(row, 1, 'Work(Day)', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
                worksheet.write(row, 2, 'Late(Day)', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
                worksheet.write(row, 3, 'Late(min)', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
                worksheet.write(row, 4, 'Absent(Day)', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
                worksheet.write(row, 5, 'Total Checkin', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
                worksheet.write(row, 6, 'Total Checkout', xlwt.easyxf('font: bold on,height 200;align: horiz right;'))
                for each in vals:
                    row += 1
                    worksheet.write(row, 0, each['employee_name'])
                    worksheet.write(row, 1, each['work_day_count'])
                    worksheet.write(row, 2, each['late_count'])
                    worksheet.write(row, 3, '%.2f' % (each['diff']), xlwt.easyxf('align: horiz right;'))
                    worksheet.write(row, 4, each['absent_count'])
                    worksheet.write(row, 5, each['count_check_in'])
                    worksheet.write(row, 6, each['count_check_out'])

        file_data = BytesIO()
        workbook.save(file_data)

        self.write({
            'state': 'get',
            'file_data': base64.encodebytes(file_data.getvalue()),
            'file_name': 'hr_attendance_report.xls'
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
