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
# from odoo.exceptions import Warning
import warnings

from lxml import etree


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    rounding_move_line = fields.Boolean(string="Rounding Move Line", copy=False)


class AccountMove(models.Model):
    _inherit = "account.move"

    round_off = fields.Float(string="Round Off", copy=False)

    value = 0.0

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                       submenu=submenu)
        if view_type == 'form':
            enable_invoice_rounding = self.env['ir.config_parameter'].sudo().get_param('enable_invoice_amount_rounding')
            if not enable_invoice_rounding:
                doc = etree.XML(res['arch'])
                if doc.xpath("//button[@name='apply_round_off']"):
                    node = doc.xpath("//button[@name='apply_round_off']")[0]
                    node.set('invisible', '1')
                if doc.xpath("//label[@for='round_off']"):
                    node = doc.xpath("//label[@for='round_off']")[0]
                    node.set('invisible', '1')
                if doc.xpath("//field[@name='round_off']"):
                    node = doc.xpath("//field[@name='round_off']")[0]
                    node.set('invisible', '1')
                if doc.xpath("//button[@name='remove_round_off']"):
                    node = doc.xpath("//button[@name='remove_round_off']")[0]
                    node.set('invisible', '1')
                res['arch'] = etree.tostring(doc)
        return res

    def remove_round_off(self):
        self.remove_rounding_line()
        self.round_off = 0.00

    def apply_round_off(self):

        invoice_line_list = []
        params = self.env['ir.config_parameter'].sudo()
        total_amount = round_off_value = 0.00
        total_amount = self.amount_untaxed + self.amount_tax
        enable_invoice_rounding = bool(params.get_param('enable_invoice_amount_rounding')),

        if enable_invoice_rounding:
            rounding_option = params.get_param('rounding_option')
            round_off_value = round(total_amount) if rounding_option == 'digits' else round(total_amount / 1, 1)
            self.round_off = (round_off_value - total_amount)
            self.add_rounding_line()

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit', 'line_ids.credit', 'line_ids.currency_id', 'line_ids.amount_currency',
        'line_ids.amount_residual', 'line_ids.amount_residual_currency',
        'line_ids.payment_id.state', 'line_ids.full_reconcile_id', 'round_off')
    def _compute_amount(self):
        super()._compute_amount()
        for move in self:
            move.amount_total = move.amount_total + move.round_off

    def add_rounding_line(self):
        invoice_line_list = []
        rounding_account_id = int(self.env['ir.config_parameter'].sudo().get_param('aspl_invoice_rounding.rounding_account_id'))
        credit = debit = 0.0
        if not self.round_off == 0.00:
            if not rounding_account_id:
                warnings.warn(f"Please select rounding account first in accounting settings.", DeprecationWarning)
                # raise Warning(_('Please select rounding account first in accounting settings.'))
            if self.round_off > 0:
                credit = self.round_off
            elif self.round_off < 0:
                debit = self.round_off
            if credit or debit:
                invoice_line_list.append((0, 0, {'name': 'Rounding Amount',
                                                 'account_id': rounding_account_id,
                                                 'price_unit': debit or credit,
                                                 'quantity': 1.00,
                                                 'tax_ids': [(6, 0, [])]}))
                self.update({
                    'invoice_date': self.invoice_date,
                    'partner_id': self.partner_id,
                    'invoice_line_ids': invoice_line_list,
                    'payment_state': 'not_paid',
                })
                for line in self.line_ids:
                    if line.account_id.id == rounding_account_id:
                        line.rounding_move_line = True

    def remove_rounding_line(self):
        rounding_account_id = int(self.env['ir.config_parameter'].sudo().get_param('aspl_invoice_rounding.rounding_account_id'))
        for line in self.line_ids:
            if line.account_id.id == rounding_account_id:
                line.sudo().unlink()