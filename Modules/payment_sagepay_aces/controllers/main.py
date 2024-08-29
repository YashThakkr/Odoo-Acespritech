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

import binascii
import logging
import pprint
from datetime import datetime

from odoo import SUPERUSER_ID, http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

_logger = logging.getLogger(__name__)

try:
    from Crypto.Cipher import AES
except ImportError:
    _logger.warning(
        'Could not find AES library, please install it using command: "pip install pycrypto".')


class SagePayController(WebsiteSale):
    # Declaring all necessary sagepay urls
    _return_url = '/payment/sagepay/return'
    _error_url = '/payment/sagepay/error'

    @http.route([
        '/payment/sagepay/return',
        '/payment/sagepay/error'
    ], type='http', auth='public', website=True)
    def sagepay_return(self, **post):
        """ SagePay."""
        request.website.sale_reset()
        _logger.info('SagePay: entering form_feedback with post data %s',
                     pprint.pformat(post))  # debug
        provider = request.env['payment.provider'].sudo().search(
            [('code', '=', "sagepay_aces")])

        # -------------Decrypt-------------
        def unpad(s):
            return s[0:-ord(s.decode("utf-8")[-1])]
        if post:
            enc = binascii.unhexlify(post.get('crypt').lstrip('@'))
            iv = enc[:16]
            cipher = AES.new((provider.key).encode("utf8"),
                             AES.MODE_CBC, (provider.key).encode("utf8"))
            responsetext = unpad(cipher.decrypt(enc)).decode("utf-8")
            response_data = responsetext.split('&')
            orderid = responsetext.split(
                '&')[0].split('-')[1].replace('_', '/')
            # Dictionary of decrypted data
            post_data = {'orderid': orderid}
            for i in range(0, len(response_data)-1):
                data = response_data[i+1].split('=')
                post_data.update({data[0]: data[1]})
            order_record = request.env['sale.order'].sudo().search(
                [('name', '=', orderid)])
            # Update Post Data
            post_data.update({'sale_order': order_record})
            tx_id = request.env['payment.transaction'].sudo().search(
                [('reference', 'ilike', orderid)], limit=1, order='id desc')
            if tx_id:
                tx_id._process_notification_data(post_data)
                if post_data.get('Status') == 'OK':
                    _logger.info('Sagepay_aces: validated data')
            elif not tx_id:
                _logger.warning(
                    'Sagepay_aces: answered failed on data verification')
            else:
                _logger.warning(
                    'Sagepay_aces: An error occurred during the transaction.')
        return request.redirect('/payment/status')

    def sagepay_aces_payment_transaction(self, post, order_record, date_create):
        values = {}
        tx_id = request.env['payment.transaction'].sudo().search(
            [('reference', '=', post.get('orderid', ''))])
        if not tx_id:
            search_merchantID = request.env['payment.provider'].sudo().search(
                [('code', '=', "sagepay_aces")])
            currency_id = request.env.user.company_id.currency_id.id
            if order_record:
                try:
                    values.update({
                        'reference': post.get('orderid', ''),
                        'provider_id': (search_merchantID and search_merchantID[0] or False),
                        'amount': order_record.amount_total,
                        'provider_reference': post.get('orderid', ''),
                        'date_create': date_create or datetime.now(),
                        'date_validate': datetime.now(),
                        'state': "draft",
                        'currency_id': (currency_id or False),
                        'partner_id': order_record.partner_id.id,
                        'partner_name': order_record.partner_id.name or False,
                        'partner_address': order_record.partner_id.street or False,
                        'partner_email': order_record.partner_id.email or False,
                        'partner_lang': order_record.partner_id.lang or False,
                        'partner_zip': order_record.partner_id.zip or False,
                        'partner_city': order_record.partner_id.city or False,
                        'partner_country_id': order_record.partner_id.country_id.id or False,
                    })
                    tx_id = request.env['payment.transaction'].sudo().create(values)
                except Exception as e:
                    pass
            else:
                try:
                    values.update({
                        'provider_reference': post.get('reference', ''),
                        'date_validate': datetime.now(),
                        'state': "draft",
                    })
                    request.env['payment.transaction'].sudo().write(
                        tx_id and tx_id[0], values)
                except Exception as e:
                    pass
        return tx_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: