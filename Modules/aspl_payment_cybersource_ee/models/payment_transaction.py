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

from odoo import api, models, _
from odoo.addons.payment import utils as payment_utils
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TxCybersource(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on transfer data.

        :param str provider: The provider of the provider that handled the transaction
        :param dict data: The transfer feedback data
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'cybersource':
            return tx

        reference = notification_data['processingValues']['reference']
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'cybersource')])
        if not tx:
            raise ValidationError(
                "Wire Transfer: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on data.

        Note: self.ensure_one()

        :param dict data: The feedback data
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != "cybersource":
            return

        self._set_done()
        if self.tokenize:
            token = self.env['payment.token'].create({
                'provider_id': self.provider_id.id,
                'payment_details': payment_utils.build_token_name(payment_details_short=notification_data['cc_cvc']),
                'partner_id': self.partner_id.id,
                'provider_ref': 'fake provider reference',
                'verified': True,
            })
            self.token_id = token.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: