# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PayslipPaymentWizard(models.TransientModel):
    _name = 'payslip.payment.wizard'
    _description = "Payslip Payment Wizard"

    journal_id = fields.Many2one('account.journal', 'Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    payment_date = fields.Date('Payment Date', required=True)
    payment_line_ids = fields.One2many('payslip.payment.line', 'payment_id', 'Payment Lines')

    @api.model
    def default_get(self, fields):
        res = super(PayslipPaymentWizard, self).default_get(fields)
        if self._context and self._context.get('active_ids'):
            payslip_ids = self.env['hr.payslip'].browse(self._context['active_ids'])
            payslip_line_obj = self.env['hr.payslip.line']
            lines = []
            for payroll in payslip_ids:
                employee_id = payroll.employee_id.id
                payslip_name = payroll.name
                payslip_number = payroll.number
                due_amount = payslip_line_obj.search(
                    [('id', 'in', payroll.line_ids.ids), ('category_id.code', 'in', ['NET'])]).total
                if 'payment_line_ids' in fields:
                    lines.append({
                        'employee_id': employee_id,
                        'payslip_name': payslip_name,
                        'payslip_number': payslip_number,
                        'payslip_due_amount': due_amount,
                        'name': payslip_name,
                        'number': payslip_number,
                        'due_amount': due_amount - payroll.transfer_amount,
                        'transfer_amount_value': payroll.transfer_amount,
                        'transfer_amount': payroll.transfer_amount,
                    })
                res['payment_line_ids'] = [(0, 0, x) for x in lines]
        return res

    def do_payslip_payment(self):
        payslip_id = self.env['hr.payslip'].browse(self._context['active_id'])
        for record in self:
            line_ids = []
            for line in record.payment_line_ids:
                if line.paid_amount > line.due_amount:
                    raise UserError(_('You plan to paid %s but your due amount %s.') % \
                                    (line.paid_amount, line.due_amount))
                if line.paid_amount <= 0:
                    raise UserError(
                        _('Please add the Amount To Pay for the Payment. It should be different from zero.'))
                date = record.payment_date
                move_dict = {
                    'narration': line.name,
                    'ref': line.number,
                    'journal_id': record.journal_id.id,
                    'date': date,
                }
                amount = line.paid_amount
                # rest_amount = payslip_id.line_ids.amount - self.payment_line_ids.paid_amount
                debit_account_id = record.journal_id.default_account_id.id
                default_account = self.env['ir.property']._get('property_account_receivable_id', 'res.partner')
                credit_account_id = default_account.id

                if credit_account_id:
                    debit_line = (0, 0, {
                        'name': line.payslip_name,
                        'account_id': credit_account_id,
                        'journal_id': record.journal_id.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                    })
                    line_ids.append(debit_line)

                if debit_account_id:
                    credit_line = (0, 0, {
                        'name': line.payslip_name,
                        'journal_id': record.journal_id.id,
                        'account_id': debit_account_id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                    })
                    line_ids.append(credit_line)
                payslip_id.update({
                    'transfer_amount': (line.transfer_amount_value + line.paid_amount)
                })
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            move.action_post()
            payslip_id.check_transfer_amount()


class PayslipPaymentLine(models.TransientModel):
    _name = 'payslip.payment.line'
    _description = "Payslip Payment Line"

    payment_id = fields.Many2one('payslip.payment.wizard', 'Payslip Payment')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    payslip_number = fields.Char(string='Payslip Reference', copy=False)
    payslip_name = fields.Char(string='Payslip Name')
    number = fields.Char(related='payslip_number', string='Reference', readonly=True, store=False)
    name = fields.Char(related='payslip_name', string='Name', readonly=True, store=False)
    journal_id = fields.Many2one('account.journal', 'Payment Journal', compute="compute_journal", store=True)
    payslip_due_amount = fields.Float('Payslip Due Amount')
    due_amount = fields.Float(related='payslip_due_amount', string='Due Amount', readonly=True, store=False)
    paid_amount = fields.Float('Amount To Pay', required=True)
    transfer_amount_value = fields.Float('Transfer Amount Value')
    transfer_amount = fields.Float(related='transfer_amount_value', string='Transfer Amount', readonly=True,
                                   store=False)

    @api.onchange('due_amount', 'paid_amount')
    def onchange_paid_amount(self):
        for record in self:
            if record.paid_amount > record.due_amount:
                raise UserError(_('You plan to paid %s but you only have %s.') % \
                                (record.paid_amount, record.due_amount))

    @api.depends('payment_id', 'payment_id.journal_id')
    def compute_journal(self):
        for record in self:
            record.journal_id = record.payment_id.journal_id.id
