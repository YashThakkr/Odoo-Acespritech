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

from odoo import fields, models, api, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import numpy as np
import numpy_financial as npf


class LoanCalc(models.Model):
    _name = 'loan.calc'
    _description = 'Loan Calc'

    global flag
    flag = 0

    def get_payment_data(self):
        global flag
        if not self.term:
            raise UserError(_('You must enter the term for loan.'))
        payment_list = []
        if self._context.get('active_id'):
            loan_app_rec = self.env['loan.application'].browse([self._context.get('active_id')])
            if loan_app_rec.state != 'approved':
                raise ValidationError(_("You can't create the payments because loan still not approved."))
            if loan_app_rec.state == 'approved' and flag == 0:
                flag = 1
                raise ValidationError(_('Are you sure you want to calculate the emi based on this amount %d.'
                                        % (self.loan_amount)))
            for line in self.loan_calc_line_ids:
                if line.due_date:
                    loan_due_date = line.due_date.strftime('%m-%Y')
                rate = line.interest_rate.strip('%')
                value = {
                    'original_due_date': line.due_date,
                    'due_date': line.due_date,
                    'rate': rate,
                    'principal': line.principal,
                    'interest': line.interest,
                    'total': line.total,
                    'balance_amt': line.balance_amt,
                    'loan_app_id': loan_app_rec.id,
                }
                payment_list.append((0, 0, value))
            if flag == 1:
                loan_app_rec.write({
                    'loan_payment_ids': payment_list,
                    'no_of_installment': len(payment_list),
                    'term': self.term,
                    'rate': self.loan_type_id.interest_rate,
                    'state': 'emi_calculated'
                })

    @api.depends('loan_calc_line_ids.principal', 'loan_calc_line_ids.interest')
    def _amount_all(self):
        for record in self:
            total_principal = principal = interest = 0.0
            if record.method == 'flat' and record.loan_amount and record.method and record.loan_type_id:
                for each_line in record.loan_calc_line_ids:
                    total_principal += each_line.principal
                principal = record.loan_amount
                interest = record.loan_type_id.interest_rate / 100 * record.loan_amount
                amt_disp = (float(record.term) / 12) * interest
                interest = amt_disp
            else:
                for line in record.loan_calc_line_ids:
                    principal += line.principal
                    interest += line.interest
            record.update({
                'principal_amount': principal,
                'interest_amount': interest,
                'total_amount': principal + interest,
            })

    @api.constrains('loan_type_id', 'loan_amount')
    def check_validation_exception_date_ids(self):
        if self.loan_type_id:
            if self.loan_type_id.maximum_amount < self.loan_amount:
                raise ValidationError(_('Loan amount exceed the limit %d.' % (self.loan_type_id.maximum_amount)))
            if self.loan_type_id.maximum_term < self.term:
                raise ValidationError(_('Loan term exceed the limit %d.' % (self.loan_type_id.maximum_term)))
            if self.loan_type_id.minimum_term > self.term:
                raise ValidationError(
                    _('Loan term limit should be greater then or equal to then %d.' % (self.loan_type_id.minimum_term)))
            if self.loan_type_id.minimum_amount > self.loan_amount and self.loan_amount:
                raise ValidationError(_('The amount you entered is lower than the minimum amount %d.'
                                        % (self.loan_type_id.minimum_amount)))

    @api.depends('term', 'loan_type_id', 'loan_amount', 'method')
    def compute_due_date(self):

        for record in self:
            date_list = []
            if record.method == 'reducing':
                principal = record.loan_amount
                months = record.term
                rate = record.loan_type_id.interest_rate / 100.00
                per = np.arange(months) + 1
                ipmt = npf.ipmt(rate / 12, per, months, principal)
                ppmt = npf.ppmt(rate / 12, per, months, principal)
                pmt = npf.pmt(rate / 12, months, principal)
                p = i = 0.00
                if record.loan_type_id and record.loan_type_id.interest_rate and record.method and record.loan_amount:
                    if np.allclose(ipmt + ppmt, pmt):
                        date_list.append((5, 0, 0))
                        for payment in per:
                            index = payment - 1
                            principal = principal + ppmt[index]
                            interestpd = np.sum(ipmt)
                            date = datetime.date.today() + relativedelta(months=payment)
                            date = date.replace(day=1)
                            date_list.append((0, 0, {
                                'due_date': date,
                                'principal': (ppmt[index] * -1),
                                'interest': (ipmt[index] * -1),
                                'interest_rate': str("%.2f" % ((rate / 12) * 100)) + " %",
                                'total': (ppmt[index] * -1) + (ipmt[index] * -1),
                                'balance_amt': abs(principal),
                                'method': record.method
                            }))
                elif record.loan_type_id and not record.loan_type_id.interest_rate and record.method and record.loan_amount:
                    principal = record.loan_amount
                    rate = record.loan_type_id.interest_rate / 100 * principal
                    time = float(record.term) / 12
                    months = record.term
                    per = np.arange(months) + 1
                    if time:
                        balance = ((record.loan_amount / time + rate) / 12) * record.term
                        date_list.append((5, 0, 0))
                        for each_term in per:
                            date = datetime.date.today() + relativedelta(months=each_term)
                            interest = principal / time + rate
                            each_month_payment = interest / 12
                            balance -= each_month_payment
                            monthly_interest = rate * time / record.term
                            monthly_principal = principal / record.term
                            date_list.append((0, 0, {
                                'due_date': date,
                                'principal': monthly_principal,
                                'interest': monthly_interest,
                                'interest_rate': str("%.2f" % (record.loan_type_id.interest_rate / 12)) + " %",
                                'total': monthly_interest + monthly_principal,
                                'balance_amt': abs(balance),
                                'method': record.method
                            }))
            elif record.method == 'flat':
                principal = record.loan_amount
                rate = record.loan_type_id.interest_rate / 100 * principal
                time = float(record.term) / 12
                months = record.term
                per = np.arange(months) + 1
                if time:
                    balance = ((record.loan_amount / time + rate) / 12) * record.term
                    date_list.append((5, 0, 0))
                    for each_term in per:
                        date = datetime.date.today() + relativedelta(months=each_term)
                        if record.loan_type_id and record.method and record.term and record.loan_amount:
                            interest = record.loan_amount / time + rate
                            each_month_payment = interest / 12
                            balance -= each_month_payment
                            monthly_interest = rate * time / record.term
                            monthly_principal = record.loan_amount / record.term
                            date_list.append((0, 0, {
                                'principal': monthly_principal,
                                'due_date': date,
                                'interest': monthly_interest,
                                'interest_rate': str("%.2f" % (record.loan_type_id.interest_rate / 12)) + " %",
                                'total': monthly_interest + monthly_principal,
                                'balance_amt': abs(balance),
                                'method': record.method
                            }))
            record.loan_calc_line_ids = date_list

    loan_amount = fields.Float(string="Loan Amount")
    principal_amount = fields.Monetary(string="Principal", store=True, readonly=True, compute='_amount_all')
    interest_amount = fields.Monetary(string="Interest", store=True, readonly=True, compute='_amount_all')
    total_amount = fields.Monetary(string="Total", store=True, readonly=True, compute='_amount_all')
    term = fields.Integer("Term")
    loan_type_id = fields.Many2one('loan.type', string="Loan Type")
    loan_calc_line_ids = fields.One2many('loan.calc.line', 'loan_calc_id', string="Loan Type ", readonly=False,
                                         compute="compute_due_date", store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, store=True)
    method = fields.Selection([
        ('flat', 'Flat'),
        ('reducing', 'Reducing')], string="Method", default='reducing')


class LoanCalcLine(models.Model):
    _name = 'loan.calc.line'
    _description = 'Loan Calc Line'

    loan_calc_id = fields.Many2one('loan.calc', string="Loan Calculator")
    currency_id = fields.Many2one('res.currency', related='loan_calc_id.currency_id', readonly=True, store=True)
    due_date = fields.Date(string="Due Date", readonly=True)
    principal = fields.Monetary("Principal", readonly=True)
    interest = fields.Monetary("Interest", readonly=True)
    balance_amt = fields.Float("Balance", readonly=True)
    interest_rate = fields.Char("Interest Rate", readonly=True)
    total = fields.Monetary("Total", readonly=True)
    method = fields.Selection([('flat', 'Flat'), ('reducing', 'Reducing')],
                              string="Method", readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
