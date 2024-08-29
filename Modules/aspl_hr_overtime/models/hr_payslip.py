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

from datetime import datetime, timedelta
from odoo import fields, models, api, exceptions, _


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        self.compute_sheet()
        overtime_id = self.env['hr.employee.overtime']
        for line in self.employee_overtime_line_ids:
            line.update({'payslip_id': self.id})
            line.overtime_id.update({'state': 'paid', 'payslip_id': self.id})
        self.update({'state': 'done', 'paid': True})
        return res

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_employee_overtime_ids(self):
        config_id = self.env['res.config.settings'].search([], limit=1, order="id desc")
        if not config_id.payslip_date_range:
            overtime_ids = self.env['overtime.line'].sudo().search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'approved')
            ])
        else:
            overtime_ids = self.env['overtime.line'].sudo().search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'approved'),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
            ])
        self.employee_overtime_line_ids = overtime_ids

    employee_overtime_ids = fields.One2many('hr.employee.overtime', 'payslip_id',
                                            string='Penalty')
    employee_overtime_line_ids = fields.One2many('overtime.line', 'payslip_id',
                                                 compute='compute_employee_overtime_ids',
                                                 string='Penalty')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
