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

from datetime import date

from odoo import fields, models, _
from odoo.exceptions import UserError


class disburse_amt_wiz(models.Model):
    _name = 'disburse.amt.wiz'

    cheque_no = fields.Char(string="Memo", required=True, size=10)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    date = fields.Date(string="Payment Date", default=date.today(), required=True)
    account_id = fields.Many2one('account.account', string="Account", required=True,
                                 domain=[('account_type', '=', 'asset_receivable')])

    def disburse(self):
        adv_req_id = self.env['hr.advance.salary.request'].browse(self._context.get('active_id'))
        move_line = []
        # journal_id = self.env['account.journal'].browse([('type', '=', 'bank')], limit=1)
        journal_id = self.journal_id
        # payable_acc_id = self.env['account.account'].search([('user_type_id.type', '=', 'payable')], limit=1)
        payable_acc_id = journal_id.default_account_id
        rec_acc_id = self.account_id
        partner = False
        if adv_req_id.employee_id.user_id:
            if adv_req_id.employee_id.user_id.partner_id.property_account_receivable_id:
                partner = adv_req_id.employee_id.user_id.partner_id.id

        if not journal_id:
            raise UserError(_('Please create the journal for bank type.'))

        move_line.append((0, 0, {'account_id': rec_acc_id.id,
                                 'name': '/',
                                 'debit': adv_req_id.approved_amt,
                                 'credit': 0,
                                 'partner_id': partner}))
        move_line.append((0, 0, {'account_id': payable_acc_id.id,
                                 'name': '/',
                                 'debit': 0,
                                 'credit': adv_req_id.approved_amt,
                                 'partner_id': partner}))
        move_id = self.env['account.move'].create({
            'date': self.date,
            'journal_id': journal_id.id,
            'ref': adv_req_id.name,
            'line_ids': move_line,
            'cheque_ref': self.cheque_no
        })
        move_id.action_post()
        adv_req_id.write({'state': 'paid', 'move_id': move_id.id, 'disburse_date': date.today()})
        return True

    _sql_constraints = [('cheque_no_uniq', 'unique(cheque_no)',
                         'Memo(Cheque Number) should be unique.')]
