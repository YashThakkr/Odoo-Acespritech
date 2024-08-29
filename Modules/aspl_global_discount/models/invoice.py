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


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('amount_total', 'discount_rate', 'discount_type')
    def _compute_net_total(self):
        for each in self:
            if each.amount_total > 0:
                if each.discount_type == 'fixed_amount':
                    if each.discount_rate <= each.amount_total:
                        each.discount = each.discount_rate
                    else:
                        raise UserError(_("Discount Cannot be more than Total"))
                elif each.discount_type == 'percentage_discount':
                    if each.discount_rate <= 100:
                        each.discount = (each.amount_total * each.discount_rate) / 100
                    else:
                        raise UserError(_("Discount rate cannot be more than 100%"))
            each.net_total = each.amount_total - each.discount

    discount_type = fields.Selection([('fixed_amount', 'Fixed Amount'),
                                      ('percentage_discount', 'Percentage')],
                                     string="Discount Type")
    discount_rate = fields.Float(string="Discount Rate")
    discount = fields.Monetary(string="Discount", compute='_compute_net_total')
    net_total = fields.Monetary(string="Net Total", compute='_compute_net_total')

    def action_post(self):
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(AccountMove, self).action_post()
        down_payment_lines = self.line_ids.filtered(lambda line: line.sale_line_ids.is_downpayment)
        for line in down_payment_lines:

            if not line.sale_line_ids.display_type:
                line.sale_line_ids._compute_name()

            try:
                line.sale_line_ids.tax_id = line.tax_ids
                if all(line.tax_ids.mapped('price_include')):
                    line.sale_line_ids.price_unit = line.price_unit
                else:
                    # To keep positive amount on the sale order and to have the right price for the invoice
                    # We need the - before our untaxed_amount_to_invoice
                    line.sale_line_ids.price_unit = -line.sale_line_ids.untaxed_amount_to_invoice
            except UserError:
                # a UserError here means the SO was locked, which prevents changing the taxes
                # just ignore the error - this is a nice to have feature and should not be blocking
                pass
        return res

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state')
    def _compute_amount(self):
        for move in self:
            total_untaxed, total_untaxed_currency = 0.0, 0.0
            total_tax, total_tax_currency = 0.0, 0.0
            total_residual, total_residual_currency = 0.0, 0.0
            total, total_currency = 0.0, 0.0

            for line in move.line_ids:
                if move.is_invoice(True):
                    # === Invoices ===
                    if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type in ('product', 'rounding'):
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == 'payment_term':
                        # Residual amount.
                        total_residual += line.amount_residual
                        # total_residual_currency += line.amount_residual_currency
                        print('\n\n amount_residual_currency==', line.amount_residual_currency)
                        total_residual_currency += move.amount_total - move.discount
                        print('\n\n total_residual_currency==', total_residual_currency)
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            sign = move.direction_sign
            move.amount_untaxed = sign * total_untaxed_currency
            move.amount_tax = sign * total_tax_currency
            move.amount_total = sign * total_currency
            move.amount_residual = -sign * total_residual_currency
            print('\n\n move.amount_residual==', move.amount_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual
            move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(
                    sign * move.amount_total)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'


    def _get_total_amount_using_same_currency(self, batch_result, early_payment_discount=True):
        if self.env.context.get('active_id'):
            invoice_id = self.env['account.move'].browse(int(self.env.context.get('active_id')))
        self.ensure_one()
        amount = 0.0
        mode = False
        for aml in batch_result['lines']:
            if early_payment_discount and aml._is_eligible_for_early_payment_discount(aml.currency_id,
                                                                                      self.payment_date):
                amount += aml.discount_amount_currency
                mode = 'early_payment'
            else:
                if invoice_id and invoice_id.discount > 0:
                    amount += aml.amount_residual_currency - invoice_id.discount
                else:
                    amount += aml.amount_residual_currency
        return abs(amount), mode

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
