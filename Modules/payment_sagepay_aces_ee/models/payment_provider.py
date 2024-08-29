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

from odoo import SUPERUSER_ID, _, fields, models
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
        return self.env.ref('payment_sagepay_aces_ee.payment_method_sagepay').id

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
        """
        This helps to encrypt the transaction details into AES encrypted.

        :param DICT values: Transaction values
        :return: Template render value is been return
        """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        values = dict(values)
        if self.key and self.vendor and self.vps_protocol:
            currency = self.env['res.currency'].sudo().browse(
                values.get('currency_id'))
            partner_id = self.env['res.partner'].sudo().browse(
                values.get('partner_id'))
            # Chipertext must same as below avoid unnecessary space
            # Currency and country must be in GB or EURO
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
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
