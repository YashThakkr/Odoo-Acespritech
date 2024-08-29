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

from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    loan_payment_ids = fields.One2many('loan.payment', 'payslip_id', compute='_compute_loan',
                                       string='Loan EMI')

    def action_payslip_done(self):
        payment_id = self.env['loan.payment']
        for each in self.loan_payment_ids:
            payment_ids = payment_id.search([('id', '=', each.id)])
            for each_id in payment_ids:
                if not each_id.payslip_id:
                    each_id.update({'state': 'paid', 'payslip_id': self.id})
        return super(HrPayslip, self).action_payslip_done()

    def refund_sheet(self):
        copied_payslips = self.env['hr.payslip']
        for payslip in self:
            copied_payslip = payslip.copy({
                'credit_note': True,
                'name': _('Refund: %(payslip)s', payslip=payslip.name),
                'edited': True,
                'state': 'verify',
            })

            for wd in copied_payslip.worked_days_line_ids:
                wd.number_of_hours = -wd.number_of_hours
                wd.number_of_days = -wd.number_of_days
                wd.amount = -wd.amount
            for line in copied_payslip.line_ids:
                if line.code == 'EMI':
                    line.amount = 0
                else:
                    line.amount = -line.amount
            copied_payslips |= copied_payslip
        copied_payslips.action_payslip_done()
        loans_emis = self.env['loan.payment'].search([('employee_id', '=', self.employee_id.id),
                                                      ('due_date', '>=', self.date_from),
                                                      ('due_date', '<=', self.date_to),
                                                      ('payslip_id', '=', self.id),
                                                      ('state', '=', 'paid'),
                                                      ('loan_app_id.state', '=', 'paid')])

        for loan in loans_emis:
            loan.write({'state': 'draft', 'payslip_id': False})

        formview_ref = self.env.ref('hr_payroll.view_hr_payslip_form', False)
        treeview_ref = self.env.ref('hr_payroll.view_hr_payslip_tree', False)
        return {
            'name': ("Refund Payslip"),
            'view_mode': 'tree, form',
            'view_id': False,
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', copied_payslips.ids)],
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'),
                      (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_loan(self):
        for payroll in self:
            loans_emis = self.env['loan.payment'].search([('employee_id', '=', payroll.employee_id.id),
                                                          ('due_date', '>=', payroll.date_from),
                                                          ('due_date', '<=', payroll.date_to),
                                                          ('state', '=', 'draft'),
                                                          ('loan_app_id.state', '=', 'paid')])

            payroll.loan_payment_ids = loans_emis




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: