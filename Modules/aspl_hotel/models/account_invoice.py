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

from odoo import api, fields, models ,_

from datetime import date
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    is_folio_invoice = fields.Boolean(string="Folio Invoice")
    folio_id = fields.Many2one('hotel.folio', string="Folio No")
    vendor_commission_ids = fields.One2many('agent.commission', 'invoice_id')
    discount_type = fields.Selection([('fixed_amount', 'Fixed Amount'),
                                      ('percentage_discount', 'Percentage')],
                                     string="Discount Type")
    discount_rate = fields.Float(string="Discount Rate")
    discount = fields.Monetary(string="Discount", compute='_compute_net_total')
    net_total = fields.Monetary(string="Net Total", compute='_compute_net_total')
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch(),
    #                             states={'draft': [('readonly', False)]})
    pickup_drop_invoice = fields.Boolean()
    walk_in_id = fields.Many2one('walk.in.detail', string="Walk In No")

    @api.depends('discount_rate', 'amount_total', 'discount_type')
    def _compute_net_total(self):
        for invoice in self:
            if invoice.amount_total:
                if invoice.discount_type == 'fixed_amount':
                    if invoice.discount_rate <= invoice.amount_total:
                        invoice.discount = invoice.discount_rate
                    else:
                        raise UserError(_("Discount Cannot be more than Total"))
                if invoice.discount_type == 'percentage_discount':
                    if invoice.discount_rate <= 100:
                        invoice.discount = (invoice.amount_total * invoice.discount_rate) / 100
                    else:
                        raise UserError(_("Discount rate cannot be more than 100%"))
            invoice.net_total = (invoice.amount_total - invoice.discount)

    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        print("\n\n\n action_move_create")
        account_move = self.env['account.move']
        for invoice in self:
            print("\n\n\n invoice")

            if not invoice.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not invoice.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if invoice.move_id:
                continue

            ctx = dict(self._context, lang=invoice.partner_id.lang)

            if not invoice.date_invoice:
                invoice.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            if not invoice.date_due:
                invoice.with_context(ctx).write({'date_due': invoice.date_invoice})
            company_currency = invoice.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            move_line = invoice.invoice_line_move_line_get()
            print("\n\n\n move_line",move_line)
            move_line += invoice.tax_line_move_line_get()

            diff_currency = invoice.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, move_line = invoice.with_context(ctx).compute_invoice_totals(company_currency, move_line)
            name = invoice.name or '/'
            if invoice.payment_term_id:
                totlines = \
                    invoice.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(
                        total,invoice.date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = invoice._get_currency_rate_date()
                for i, t in enumerate(totlines):
                    if invoice.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], invoice.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    move_line.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': invoice.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and invoice.currency_id.id,
                        'invoice_id': invoice.id
                    })
            else:
                move_line.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': invoice.account_id.id,
                    'date_maturity': invoice.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and invoice.currency_id.id,
                    'invoice_id': invoice.id
                })
            part = self.env['res.partner']._find_accounting_partner(invoice.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in move_line]
            line = invoice.group_lines(move_line, line)
            discount_account_id = False
            if not invoice.discount == 0.0:
                if invoice.type in ('out_invoice', 'in_refund'):
                    discount_account_id = int(
                        self.env['ir.config_parameter'].sudo().get_param('aspl_hotel.discount_account_id'))
                if not discount_account_id:
                    raise UserError(_('Please select discount account first in hotel settings.'))
                if discount_account_id:
                    line += [(0, 0, {'name': 'Discount Amount',
                                     'price': invoice.discount,
                                     'account_id': discount_account_id,
                                     'credit': invoice.discount if invoice.type in ('in_invoice', 'out_refund') else 0.0,
                                     'debit': invoice.discount if invoice.type in ('out_invoice', 'in_refund') else 0.0,
                                     'partner_id': invoice.partner_id.id,
                                     'currency_id': invoice.currency_id.id,
                                     'invoice_id': invoice.id,
                                     })]
            journal = invoice.journal_id.with_context(ctx)
            line = invoice.finalize_invoice_move_lines(line)

            date = invoice.date or invoice.date_invoice
            move_vals = {
                'ref': invoice.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': invoice.comment,
            }
            ctx['company_id'] = invoice.company_id.id
            ctx['invoice'] = invoice
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            invoice.with_context(ctx).write(vals)
        return True

    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_purchase_ids(self):
        """
        The purpose of the method is to define a domain for the available
        purchase orders.
        """
        result = {}
        # A PO can be selected only if at least one PO line is not already in the invoice
        purchase_line_ids = self.invoice_line_ids.mapped('purchase_line_id')
        purchase_ids = self.invoice_line_ids.mapped('purchase_id').filtered(
            lambda r: r.order_line <= purchase_line_ids)
        result['domain'] = {'purchase_id': [
            ('invoice_status', '=', 'to invoice'),
            ('partner_id', 'child_of', self.partner_id.id),
            ('id', 'not in', purchase_ids.ids),
            # ('branch_id', '=', self.branch_id.id)
        ]}
        return result

    @api.model
    def _get_refund_copy_fields(self):
        copy_fields = ['company_id', 'user_id', 'fiscal_position_id']
        # copy_fields = ['company_id', 'user_id', 'fiscal_position_id', 'branch_id']
        return self._get_refund_common_fields() + self._get_refund_prepare_fields() + copy_fields

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id
        # self.branch_id = self.purchase_id.branch_id.id

        new_lines = self.env['account.move.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.payment_term_id = self.purchase_id.payment_term_id
        self.env.context = dict(self.env.context, from_purchase_order_change=True)
        self.purchase_id = False
        return {}


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # branch_id = fields.Many2one('company.branch', string="Branch", related='move_id.branch_id',
    #                             store=True)
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order ", store=True,
                                  related='purchase_line_id.order_id')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())

    def action_validate_invoice_payment(self):
        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(
                _("This method should only be called to process a single invoice's payment."))
        # self.branch_id = self.invoice_ids[0].branch_id.id
        return self.post()


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        active_ids = self.env.context.get('active_id')
        active_invoice_id = self.env['account.move'].browse(active_ids)
        if res and active_invoice_id.state == 'posted':
            amount = 0.0
            if active_invoice_id and active_invoice_id.folio_id.walk_in_id.agent_id:
                for line in active_invoice_id.folio_id.walk_in_id.agent_id.agent_commission_ids:
                    amount = active_invoice_id.amount_total * line.commission / 100 if line.calculation == 'percentage' else line.commission
                agent_detail = {'agent_id': active_invoice_id.folio_id.walk_in_id.agent_id.id,
                                'name': active_invoice_id.name,
                                'commission_date': date.today(),
                                'state': 'draft',
                                'amount': amount,
                                'invoice_id': active_invoice_id.id
                                }
                self.env['agent.commission'].create(agent_detail)
        pickup_drop_id = self.env['hotel.pickup.drop'].search([('invoice_id','=', active_invoice_id.id)])
        pickup_drop_id.state = 'done'
        return res

    # def _create_payment_vals_from_batch(self, batch_result):
    #     res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(batch_result)
    #     if self.env.context.get('active_model') == 'account.move' and self.env.context.get(
    #             'active_ids'):
    #         move_ids = self.env['account.move'].search(
    #             [('id', 'in', self.env.context.get('active_ids'))])
    #         check_branch_diff = set([x.branch_id.id for x in move_ids])
    #         if len(check_branch_diff) > 1:
    #             raise UserError(_("Cannot create payment for different branches."))
    #         elif len(check_branch_diff) == 1:
    #             res['branch_id'] = move_ids.mapped('branch_id').ids[0]
    #     return res

    # def _create_payment_vals_from_wizard(self):
    #     res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
    #     if self.env.context.get('active_model') == 'account.move' and self.env.context.get(
    #             'active_ids'):
    #         move_ids = self.env['account.move'].search(
    #             [('id', 'in', self.env.context.get('active_ids'))])
    #         check_branch_diff = set([x.branch_id.id for x in move_ids])
    #         if len(check_branch_diff) > 1:
    #             raise UserError(_("Cannot create payment for different branches."))
    #         elif len(check_branch_diff) == 1:
    #             res['branch_id'] = move_ids.mapped('branch_id').ids[0]
    #     return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: