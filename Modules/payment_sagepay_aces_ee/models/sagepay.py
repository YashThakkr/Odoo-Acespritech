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

import codecs
import logging
import time

from odoo import fields, models
from odoo.addons.payment.models.payment_provider import ValidationError
from odoo.addons.payment_sagepay_aces_ee.controllers.main import SagePayController

_logger = logging.getLogger(__name__)

try:
    from Crypto.Cipher import AES
except ImportError:
    _logger.warning(
        'Could not find AES library, please install it using command: "pip install pycrypto" and "pip install pycryptodome".')


class ProviderSagePay(models.Model):
    _inherit = 'payment.provider'

    vps_protocol = fields.Char(
        'VPS Protocol', required_if_provider='sagepay_aces')
    vendor = fields.Char('Vendor', required_if_provider='sagepay_aces')
    key = fields.Char('Key', required_if_provider='sagepay_aces')
    code = fields.Selection(selection_add=[('sagepay_aces', 'SagePay')], ondelete={
                                'sagepay_aces': 'set default'})

    def _get_default_payment_method_id(self, code):
        self.ensure_one()
        if self.code != 'sagepay_aces':
            return super(ProviderSagePay, self)._get_default_payment_method_id(code)
        return self.env.ref('aspl_payment_cybersource.payment_method_sagepay').id

    def _get_sagepay_aces_urls(self):
        """ SagePay URLs """
        if self.state == 'enabled':
            environment = 'live'
        else:
            environment = 'test'
        return "https://%s.sagepay.com/gateway/service/vspform-register.vsp" % str(environment)

    def _get_providers(self):
        providers = super(ProviderSagePay, self)._get_providers()
        providers.append(['sagepay_aces', 'SagePay'])
        return providers

    def sagepay_aces_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        values = dict(values)
        if self.key and self.vendor and self.vps_protocol:
            currency = self.env['res.currency'].sudo().browse(
                values.get('currency_id'))
            partner_id = self.env['res.partner'].sudo().browse(
                values.get('partner_id'))
            #Chipertext must same as below avoid unnecessary space 
            ciphertext = '''VendorTxCode={VendorTxCode}&Amount={Amount}&Currency={Currency}&Description={Description}&CustomerName={CustomerName}&CustomerEMail={CustomerEMail}&BillingSurname={BillingSurname}&BillingFirstnames={BillingFirstnames}&BillingAddress1={BillingAddress1}&BillingCity={BillingCity}&BillingPostCode={BillingPostCode}&BillingCountry={BillingCountry}&BillingPhone={BillingPhone}&DeliveryFirstnames={DeliveryFirstnames}&DeliverySurname={DeliverySurname}&DeliveryAddress1={DeliveryAddress1}&DeliveryCity={DeliveryCity}&DeliveryPostCode={DeliveryPostCode}&DeliveryCountry={DeliveryCountry}&DeliveryPhone={DeliveryPhone}
            '''.format(VendorTxCode="TxCode-" + str(values.get('reference')).replace('/', '_') + '-' + str(time.strftime("%Y%m%d%H%M%S")),
                       Amount=values['amount'],
                       Currency=currency.name or '',
                       Description=str(values['reference']) +
                       str(time.strftime("%Y%m%d%H%M%S")),
                       CustomerName=partner_id.name,
                       CustomerEMail=partner_id.email,
                       BillingSurname=partner_id.name,
                       BillingFirstnames=partner_id.name,
                       BillingAddress1=partner_id.street +
                       (partner_id.street2 if partner_id.street2 else ''),
                       BillingCity=partner_id.city,
                       BillingPostCode=partner_id.zip,
                       BillingCountry=partner_id.country_id.code,
                       BillingPhone=partner_id.phone or partner_id.mobile or '',
                       DeliverySurname=partner_id.name,
                       DeliveryFirstnames=partner_id.name,
                       DeliveryAddress1=partner_id.street +
                       (partner_id.street2 if partner_id.street2 else ''),
                       DeliveryCity=partner_id.city,
                       DeliveryPostCode=partner_id.zip,
                       DeliveryCountry=partner_id.country_id.code,
                       DeliveryPhone=partner_id.phone or partner_id.mobile or '')
            ciphertext = ciphertext + '&SuccessURL=%s&FailureURL=%s' % (str(base_url + SagePayController._return_url),
                                                                        str(base_url + SagePayController._error_url))
            def pad(s): return bytes(s + (16 - len(s) %
                                          16) * chr(16 - len(s) % 16), 'utf-8')
            cipher = AES.new((self.key).encode("utf8"),
                             AES.MODE_CBC, (self.key).encode("utf8"))
            result = codecs.encode(cipher.encrypt(pad(ciphertext)), 'hex')
            values.update({
                'VPSProtocol': '3.0',
                'TxType': 'PAYMENT',
                'Vendor': self.vendor,
                'Crypt': '@' + result.decode('utf-8').upper(),
            })
        return values

    def sagepay_aces_get_form_action_url(self, id):
        provider = self.browse(id)
        return self._get_sagepay_aces_urls(provider.environment)['sagepay_aces_form_url']


class TxSagePay(models.Model):
    _inherit = 'payment.transaction'

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Alipay-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'sagepay_aces':
            return res
        rendering_values = self.provider_id.sagepay_aces_form_generate_values(
            processing_values)
        processing_values.update(rendering_values)
        processing_values.update({
            'api_url': self.provider_id._get_sagepay_aces_urls(),
            'provider': self.provider_id
        })
        return processing_values

    def _sagepay_aces_form_get_tx_from_data(self, data):
        # reference = data.get('reference')
        reference = data.get('orderid')
        if not reference:
            error_msg = 'SagePay: received data with missing reference (%s) or txn_id (%s)' % (
                reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        tx_ids = self.env['payment.transaction'].sudo().search(
            [('reference', '=', reference)])
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'SagePay: received data for reference %s' % (reference)
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return self.browse(tx_ids[0])

    def _sagepay_aces_form_get_invalid_parameters(self, tx, data):
        invalid_parameters = []
        if tx.provider_reference and data.get('orderid') != tx.provider_reference:
            invalid_parameters.append(
                ('Transaction Id', data, tx.provider_reference))
        return invalid_parameters

    def _sagepay_aces_form_validate(self, tx, data):
        status = data.get('Status')
        write_data = {
            'status': data.get('Status'),
            'status_detail': data.get('StatusDetail'),
            'vpstxid': data.get('VPSTxId'),
            'provider_reference': data.get('orderid')
        }
        if status == "OK":
            _logger.info(
                'Validated SagePay payment for tx %s: set as done' % (tx.reference))
            write_data.update(
                state='done', state_message='Successful', date_validate=fields.datetime.now())
            return tx.write(write_data)
        elif status in ["NOTAUTHED", "MALFORMED", "INVALID", "ABORT", "REJECTED", "AUTHENTICATED", "REGISTERED"]:
            _logger.info(
                'Received notification for SagePay payment %s: set as failed' % (tx.reference))
            write_data.update(
                state='cancel', state_message=data.get('StatusDetail', ''))
            # Update quotation status
            if data.get('sale_order'):
                data.get('sale_order').write({'state': 'cancel'})
            return tx.write(write_data)
        else:
            error = 'Received unrecognized status for SagePay payment %s: %s, set as error' % (
                tx.reference, status)
            _logger.info(error)
            write_data.update(state='error', state_message=error)
            return tx.write(write_data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
