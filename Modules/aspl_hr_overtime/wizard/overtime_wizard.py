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
from datetime import datetime, date, timedelta
from io import BytesIO
from dateutil.relativedelta import relativedelta
import xlwt
import base64
from odoo.exceptions import UserError


class WizardOvertime(models.TransientModel):
    _name = "wizard.overtime"
    _description = "Overtime wizard"

    start_date = fields.Date(default=date.today().replace(day=1))
    end_date = fields.Date(default=(date.today() + relativedelta(months=1,
                                                                 day=1)) - timedelta(1))
    employee_ids = fields.Many2many('hr.employee')
    payslip_detail = fields.Boolean()
    file_data = fields.Binary(string='File')
    file_name = fields.Char(string='File Name', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')

    def overtime(self, ):
        dic_overtime = {}
        lst_overtime = []
        if not self.employee_ids:
            employee = [emp_id.id for emp_id in self.env['hr.employee'].search([])]
        else:
            employee = [emp_id.id for emp_id in self.employee_ids]
        overtime_ids = self.env['hr.employee.overtime'].search(
            [('date', '>=', self.start_date), ('date', '<=', self.end_date),
            ('employee_id', 'in', employee)])
        for overtime in overtime_ids:
            dic_overtime = {'name': overtime.name}
            lst_overtime.append(dic_overtime)
        return lst_overtime

    def summary_data(self, ):
        if not self.employee_ids:
            employee = [emp_id.id for emp_id in self.env['hr.employee'].search([])]
        else:
            employee = [emp_id.id for emp_id in self.employee_ids]
        sql_overtime = """select line.date, line.employee_id, line.overtime, line.overtime_id,line.ot_rate,line.description,overtime.id as overtime_id
                                  ,line.based_on,overtime.employee_id as overtime_employee,overtime.state,line.overtime_id as overtime_line_id
                                  ,overtime.payslip_id,overtime.date as overtime_date,line.overtime_minute,overtime.name
                                  from hr_employee_overtime as overtime,overtime_line as line
                                  where  line.overtime_id = overtime.id
                                  AND overtime.employee_id in %s
                                  And overtime.date >= '%s'
                                  And overtime.date <= '%s'""" % (" (%s) " % ','.join(map(str, employee)),
                                                                  str(self.start_date),
                                                                  str(self.end_date))
        self._cr.execute(sql_overtime)
        overtime_result = self._cr.dictfetchall()

        final_lst_overtime = []
        overtime_data_dic = {}
        for overtime in overtime_result:
            payslip_id = self.env['hr.payslip'].search([('id', '=', overtime.get('payslip_id'))])
            overtime_data_dic = {
                'date': overtime.get('date'),
                'name': overtime.get('name'),
                'description': overtime.get('description'),
                'based_on': overtime.get('based_on'),
                'ot_rate': overtime.get('ot_rate'),
                'overtime_minute': overtime.get('overtime_minute'),
                'overtime_id': overtime.get('overtime_id'),
                'overtime': overtime.get('overtime'),
                'state': overtime.get('state'),
                'payslip_id': payslip_id.number,
            }
            final_lst_overtime.append(overtime_data_dic)
        return final_lst_overtime

    def print_report_pdf(self):
        return self.env.ref('aspl_hr_overtime.pdf_overtime_report').report_action(self)

    def print_report_excel(self):
        self.ensure_one()
        overtime_data_dict = self.summary_data()
        overtime_nm_dic = self.overtime()
        curr_symbol = self.env.user.company_id.currency_id.symbol
        report_header = xlwt.easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        header_format = xlwt.easyxf(
            'font:height 200,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        style_filter_data = xlwt.easyxf(
            'font:bold True; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        data_format = xlwt.easyxf(
            'align: horiz left; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        if overtime_data_dict:
            workbook = xlwt.Workbook(encoding="utf-8")
            worksheet = workbook.add_sheet("Over Time Employee Report")
            worksheet.write_merge(0, 1, 0, 4, "Overtime Report", style=report_header)
            worksheet.write_merge(2, 2, 1, 1, "Start Date", style=header_format)
            worksheet.write_merge(2, 2, 2, 3, "End Date", style=header_format)
            if self.start_date:
                worksheet.write_merge(3, 3, 1, 1, str(self.start_date), style=style_filter_data)
            if self.end_date:
                worksheet.write_merge(3, 3, 2, 3, str(self.end_date), style=style_filter_data)
            worksheet.write_merge(4, 4, 1, 1, "Employee", style=header_format)
            if self.employee_ids:
                emp_nm = ', '.join(map(lambda x: (x.name), self.employee_ids))
                worksheet.write_merge(5, 5, 1, 1, emp_nm, style=style_filter_data)
            else:
                worksheet.write_merge(5, 5, 1, 1, 'All', style=style_filter_data)
            row_header = 5
            worksheet.write_merge(row_header + 2, row_header + 2, 0, 0, 'Date', style=header_format)
            worksheet.write_merge(row_header + 2, row_header + 2, 1, 1, 'Description', style=header_format)
            worksheet.write_merge(row_header + 2, row_header + 2, 2, 2, 'Type', style=header_format)
            worksheet.write_merge(row_header + 2, row_header + 2, 3, 3, 'OT.Hours', style=header_format)
            worksheet.write_merge(row_header + 2, row_header + 2, 4, 4, 'OT.Rate', style=header_format)
            if self.payslip_detail:
                worksheet.write_merge(row_header + 2, row_header + 2, 5, 5, 'OT.Payable',
                                      style=header_format)
                worksheet.write_merge(row_header + 2, row_header + 2, 6, 6, 'Status',
                                      style=header_format)
            row = row_header + 3
            row_data = row_header + 4
            for overtime in overtime_nm_dic:
                if self.payslip_detail:
                    worksheet.write_merge(row, row, 0, 6, overtime['name'], style=style_filter_data)
                else:
                    worksheet.write_merge(row, row, 0, 4, overtime['name'], style=style_filter_data)
                for val in overtime_data_dict:
                    if overtime['name'] == val['name']:
                        description = val['description'] or " "
                        worksheet.write_merge(row_data, row_data, 0, 0, str(val['date']), style=data_format)
                        worksheet.write_merge(row_data, row_data, 1, 1, description, style=data_format)
                        worksheet.write_merge(row_data, row_data, 2, 2, val['based_on'], style=data_format)
                        worksheet.write_merge(row_data, row_data, 3, 3, val['overtime'], style=data_format)
                        worksheet.write_merge(row_data, row_data, 4, 4, val['ot_rate'], style=data_format)
                        if self.payslip_detail:
                            worksheet.write_merge(row_data, row_data, 5, 5, val['payslip_id'], style=data_format)
                            worksheet.write_merge(row_data, row_data, 6, 6, val['state'], style=data_format)
                        row_data += 1
                row = row_data + 1
                row_data = row + 1
            worksheet.col(0).width = 4200
            worksheet.col(1).width = 10000
            worksheet.col(2).width = 6000
            worksheet.col(3).width = 6000
            worksheet.col(4).width = 6000
            worksheet.col(5).width = 6000
            file_data = BytesIO()
            workbook.save(file_data)
            self.write({
                'state': 'get',
                'file_data': base64.encodebytes(file_data.getvalue()),
                'file_name': 'Over Time Employee Report.xlsx'
            })
        else:
            raise UserError(_('No Record Found.'))
        return {
            'name': 'Over Time Employee Report',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
