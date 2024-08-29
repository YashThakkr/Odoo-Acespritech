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

import json
import re
from urllib.parse import urlencode
from urllib.request import build_opener, Request, HTTPHandler
from urllib.error import HTTPError, URLError
from datetime import datetime, date

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class Hobex(http.Controller):

    @http.route(['/shop/payment/failed'], type='http', auth="public", csrf=False, method=['post'], website=True)
    def payment_failed(self, **kw):
        #If Payment failed it will redirect here
        return request.render('aspl_payment_hobex.PaymentFailed',
                              {'reason': request.session['description'].capitalize()})

    @http.route(['/hobex/payment'], type='http', auth="public", csrf=False, method=['POST', 'GET'], website=True)
    def hobexpay_payment(self, **kw):
        order_id = request.session.get('sale_order_id')
        order = request.env['sale.order'].sudo().search(
            [('id', '=', order_id)])
        tx_id = request.env['payment.transaction'].sudo().search(
            [('sale_order_ids', 'in', order.ids)],
            limit=1, order='id desc')
        if not tx_id:
            tx_id = request.env['payment.transaction'].sudo().browse(int(kw.get('tx')))
        request.session['provider'] = tx_id.provider_id.code
        payment_provider = tx_id.provider_id
        url = "%s/checkouts/%s/payment" % (
            payment_provider.hobex_url, str(request.session.get('hobex_checkout_id')))
        url += '?entityId=%s' % payment_provider.hobex_entityId
        opener = build_opener(HTTPHandler)
        data = ''
        request_data = Request(url, data=urlencode(data).encode('utf-8'))
        request_data.add_header(
            'Authorization', 'Bearer ' + payment_provider.hobex_accesstoken)
        request_data.get_method = lambda: 'GET'
        try:
            response = opener.open(request_data)
            responseData = json.loads(response.read())
            responseData.update({
                'reference': tx_id.reference,
            })
            if responseData:
                request.session['description'] = responseData['result']['description']
            if responseData['result']['code'] in ['000.100.110', '000.000.000', '000.100.112']:
                return_url = '/shop/confirmation'
                if kw.get('tx') and not order_id:
                    invoice_id = request.env['account.move'].sudo().search([('name', '=', tx_id.reference.split('-')[0])])
                    return_url ='/my/invoices/%s?access_token=%s' % (invoice_id.id, invoice_id._portal_ensure_token())
                    if not invoice_id and not order_id:
                        sale_order_id = request.env['sale.order'].sudo().search([('name', '=', tx_id.reference.split('-')[0])])
                        return_url = '/my/orders/%s?access_token=%s' % (sale_order_id.id, sale_order_id._portal_ensure_token())
                if responseData.get('resultDetails') and responseData.get('resultDetails').get('ExtendedDescription'):
                    ref = responseData['resultDetails']['ExtendedDescription']
                elif responseData.get('result') and responseData.get('result').get('description'):
                    ref = responseData['result']['description']
                else:
                    ref = ''
                tx_id.provider_reference = ref
                tx_id.sudo()._handle_notification_data(
                    tx_id.provider_id.code, responseData)
                tx_id.state = 'done'
                tx_id.last_state_change = date.today()
                responseData.update({'tx': tx_id.id})
            else:
                return_url = '/shop/payment/failed'
            return request.redirect(return_url)
        except HTTPError as e:
            return json.loads(e.read())
        except URLError as e:
            return e.reason

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        payment_provider = request.env['payment.provider'].sudo().search(
            [('code', '=', request.session.get('provider'))])
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if not order or order.state != 'draft':
                request.website.sale_reset()
            # if payment_provider.code in ['hobex_credit_card', 'hobex_paypal', 'hobex_sofort']:
            #     order.action_confirm()
            return request.render("website_sale.confirmation", {'website_sale_order': order,'order':order})
        else:
            return request.redirect('/shop')


class WebsiteSale(WebsiteSale):

    @http.route('/redirect/payment/hobex', type='http', auth="public", methods=['GET', 'POST'], website=True,
                csrf=False)
    def redirect_payment_hobex(self, **kwargs):
        if not kwargs:
            return request.redirect('/shop/payment')
        else:
            request.session['provider_id'] = kwargs.get('provider_id')
            provider_id = request.env['payment.provider'].sudo().browse(
                [int(kwargs.get('provider_id'))])
            base_url = request.env['ir.config_parameter'].sudo(
            ).get_param('web.base.url')
            if request.session.get ('sale_order_id') and 'SO' in kwargs.get('so_id'):
                order = request.env['sale.order'].sudo().search(
                    [('id', '=', int(request.session.get('sale_order_id')))])
                responseData = self.request_data(provider_id.code, tx_id=None)
                payment_transaction_obj = request.env['payment.transaction'].sudo().search(
                    [('sale_order_ids', 'in', order.ids)], limit=1, order='id desc')

                transaction_dict = {'provider_id': int(kwargs.get('provider_id')),
                                    # 'type': 'server2server',
                                    # 'date': datetime.now(),
                                    'amount': order.amount_total,
                                    # 'return_url': '/shop/confirmation',
                                    'currency_id': order.currency_id.id,
                                    'provider_reference': order.name,
                                    'partner_id': order.partner_id.id,
                                    'partner_name': order.partner_id.name,
                                    'partner_lang': order.partner_id.lang,
                                    'partner_email': order.partner_id.email,
                                    'partner_zip': order.partner_id.zip,
                                    'partner_address': order.partner_id.street,
                                    'partner_city': order.partner_id.city,
                                    'partner_country_id': order.partner_id.country_id.id,
                                    'partner_phone': order.partner_id.phone,
                                    'sale_order_ids': [(6, 0, [order.id])],
                                    'reference': order.name}
                if not payment_transaction_obj:
                    payment_transaction_obj = request.env['payment.transaction'].sudo().create(
                        transaction_dict)
                request.session["payment_tx_id"] = [payment_transaction_obj.id]
                request.session["hobex_pay"] = kwargs.get('hobex_pay')
                try:
                    if responseData:
                        request.session['hobex_checkout_id'] = responseData.get(
                            'id')
                        data = {
                            'data_brand': kwargs.get('hobex_pay'),
                            'payment': responseData.get('id'),
                            'provider_id': provider_id,
                            'base_url': base_url,
                            'hobex_url': provider_id.hobex_url,
                            }
                        return request.render('aspl_payment_hobex.hobex_payment_template', data)
                except Exception as e:
                    pass
            else:
                reference = kwargs.get('so_id') # .split('-')[0]
                tx_id =  request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
                if not tx_id:
                    tx_id = request.env['payment.transaction'].sudo().search([('sale_order_ids', 'in', [reference])], limit=1)
                responseData = self.request_data(provider_id.code, tx_id)
                request.session["payment_tx_id"] = [tx_id.id]
                request.session["hobex_pay"] = kwargs.get('hobex_pay')
                try:
                    if responseData:
                        request.session['hobex_checkout_id'] = responseData.get(
                            'id')
                        data = {
                            'data_brand': kwargs.get('hobex_pay'),
                            'payment': responseData.get('id'),
                            'provider_id': provider_id,
                            'base_url': base_url,
                            'hobex_url': provider_id.hobex_url,
                            'tx_id': tx_id.id
                            }
                        return request.render('aspl_payment_hobex.hobex_payment_template', data)
                except Exception as e:
                    pass

    def request_data(self, provider, tx_id):
        payment_provider = request.env['payment.provider'].sudo().search(
            [('code', '=', provider)])
        if request.session.get('sale_order_id'):
            order = request.env['sale.order'].sudo().search(
                [('id', '=', int(request.session.get('sale_order_id')))])
            url = payment_provider.hobex_url + '/checkouts'
            amount = "{0:,.2f}".format(order.amount_total).replace(',', '')
            data = {
                'entityId': payment_provider.hobex_entityId,
                'amount': amount,
                'currency': order.currency_id.name,
                'paymentType': 'DB'
            }
        else:
            url = payment_provider.hobex_url + '/checkouts'
            amount = "{0:,.2f}".format(tx_id.amount).replace(',', '')
            data = {
                'entityId': payment_provider.hobex_entityId,
                'amount': amount,
                'currency': tx_id.currency_id.name,
                'paymentType': 'DB'
            }
        try:
            opener = build_opener(HTTPHandler)
            request_data = Request(url, data=urlencode(data).encode('utf-8'))
            request_data.add_header(
                'Authorization', 'Bearer ' + str(payment_provider.hobex_accesstoken))
            request_data.get_method = lambda: 'POST'
            response = opener.open(request_data)
            return json.loads(response.read())
        except HTTPError as e:
            return json.loads(e.read())
        except URLError as e:
            return e.reason

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
