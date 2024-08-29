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

from odoo import models,_

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Alipay-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'sagepay_aces':
            return res
        rendering_values = self.provider_id.sagepay_aces_form_generate_values(
            processing_values)
        processing_values.update(rendering_values)
        processing_values.update({
            'api_url': self.provider_id._get_sagepay_aces_urls(),
            'provider': self.provider_id
        })
        return processing_values

    def _process_notification_data(self, data):
        """ Override of payment to process the transaction based on data.

        Note: self.ensure_one()

        :param dict data: The feedback data
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(data)
        if self.provider_code != "sagepay_aces":
            return
        if data.get('Status') == 'OK':
            _logger.info('Sagepay_aces: validated data')
            if self.state != 'done':
                self._set_done()
        else:
            self._set_error(
                _("An error occurred during the processing of your payment. Please try again.")
            )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
