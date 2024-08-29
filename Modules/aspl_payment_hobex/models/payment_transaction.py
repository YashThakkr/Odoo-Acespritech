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

import logging
import re

from odoo import api, fields, models, _, SUPERUSER_ID


class PaymentTransactionmygate(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Sips-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code not in ['hobex_credit_card', 'hobex_paypal', 'hobex_sofort']:
            return res

        base_url = self.get_base_url()
        data = {
            'amount': self.amount,
            'currency': self.currency_id.name,  # The ISO 4217 code
            'currency_id': self.currency_id.id,
            'provider_id': self.provider_id.id,
            'so_id': self.sale_order_ids.id or self.reference,
            'api_url': base_url + '/redirect/payment/hobex',
        }
        return data

    def _process_notification_data(self, data):
        """ Override of payment to process the transaction based on data.

        Note: self.ensure_one()

        :param dict data: The feedback data
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        res = super(PaymentTransactionmygate,
                    self)._process_notification_data(data)
        if self.provider_code not in ['hobex_credit_card', 'hobex_paypal', 'hobex_sofort']:
            return res
        self._set_done()
        self.with_context({'hobex': True})._reconcile_after_done()

    def _reconcile_after_done(self):
        """ Override of payment to automatically confirm quotations and generate invoices. """
        if self._context.get('hobex'):
            sales_orders = self.mapped('sale_order_ids').filtered(
                lambda so: so.state in ('draft', 'sent'))
            default_template = self.env['ir.config_parameter'].sudo().get_param(
                        'sale.default_invoice_email_template')
            template_record = self.env['ir.ui.view'].sudo().browse(int(default_template))
            for tx in self:
                tx._check_amount_and_confirm_order()
            # send order confirmation mail
            sales_orders._send_order_confirmation_mail()
            # invoice the sale orders if needed
            if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice') and any(
                    so.state in ('sale', 'done') for so in self.sale_order_ids):
                self._invoice_sale_orders()
                # default_template = self.env['ir.config_parameter'].sudo().get_param(
                #     'sale.default_invoice_email_template')
                if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice') and any(
                    so.state in ('sale', 'done') for so in self.sale_order_ids):
                    for trans in self.filtered(lambda t: t.sale_order_ids.filtered(lambda so: so.state in ('sale', 'done'))):
                            trans = trans.with_company(trans.provider_id.company_id).with_context(
                                mark_invoice_as_sent=True,
                                company_id=trans.provider_id.company_id,
                            )
                            for invoice in trans.invoice_ids.with_user(SUPERUSER_ID):
                                invoice.message_post_with_source(
                                    source_ref=template_record,
                                    email_layout_xmlid='mail.mail_notification_light',
                                    subtype_xmlid='mail.mt_note'
                                )
                    self.invoice_ids.filtered(lambda inv: inv.state == 'draft').action_post()

                    # Create and post missing payments for transactions requiring reconciliation
                    for tx in self.filtered(lambda t: t.operation != 'validation' and not t.payment_id):
                        tx._create_payment()
        else:
            return super()._reconcile_after_done()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
