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
from odoo.exceptions import UserError
import datetime


class LoanType(models.Model):
    _name = 'loan.type'
    _description = 'Loan Type'

    def view_interest_history(self):
        return {
            'name': _('Change Interest Rate History'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'interest.rate.history',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('aspl_employee_loan.interest_rate_history_tree').id,
            'domain': [('loan_type_id', '=', self.id)],
            # 'context':{'default_name':self.name}
        }

    def create_interest_history(self):
        return {
            'name': _('Change Interest Rate'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'interest.rate.history',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('aspl_employee_loan.interest_rate_history_form').id,
            'target': 'new',
            'context': {'default_loan_type_id': self.id,
                        'default_rate':self.interest_rate},

        }

    @api.constrains('minimum_amount', 'maximum_amount', 'minimum_term', 'maximum_term', 'interest_rate', 'fees_amount')
    def check_amount_values(self):
        if (self.minimum_amount <= 0.0) or (self.maximum_amount <= 0.0) or (self.minimum_term <= 0.0) or \
                (self.maximum_term <= 0.0) or (self.fees_amount < 0.0):
            raise UserError(_('Please enter proper value.'))
        elif self.maximum_amount < self.minimum_amount:
            raise UserError(_('Maximum amount should be greater then minimum amount.'))
        elif self.maximum_term < self.minimum_term:
            raise UserError(_('Maximum term should be greater then minimum term.'))

    name = fields.Char("Name", required=True)
    term_condition = fields.Text("Terms and Conditions")
    minimum_amount = fields.Float("Minimum Amount", required=True)
    maximum_amount = fields.Float("Maximum Amount", required=True)
    interest_rate = fields.Float("Annual Interest Rate", required=True)
    minimum_term = fields.Integer("Min Term (In Months)", required=True)
    maximum_term = fields.Integer("Max Term (In Months)", required=True)
    fees_amount = fields.Integer("Fees Amount")
    # loan_doc_ids = fields.Many2many('loan.document', 'loan_type_id', 'loan_doc_id', string='Documents', required=True)
    app_categ_ids = fields.Many2many('applicant.category', 'loan_id', 'loan_app_categ_id', string='Applicant Category')
    method = fields.Selection([('flat', 'Flat'), ('reducing', 'Reducing')],
                              string="Method", default='reducing', required=True)


class LoanDocument(models.Model):
    _name = 'loan.document'
    _description = 'Loan Document'

    name = fields.Char("Name", required=True)


class InterestRateHistory(models.Model):
    _name = 'interest.rate.history'
    _description = 'Interest Rate History'
    _order = 'id desc'

    def save_interest(self):
        self.loan_type_id.write({'interest_rate': self.rate})

    rate = fields.Float("Rate", required=True)
    date = fields.Date("Date", default=datetime.datetime.now(), _order='date desc')
    loan_type_id = fields.Many2one('loan.type', string="Loan Type")
    # name = fields.Many2one('loan.type',required=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
