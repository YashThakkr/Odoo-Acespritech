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

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import requests
import json
import urllib.parse
from urllib.parse import urlencode
from odoo.addons.aspl_payment_bluepay.controllers.bluepay import BluePay

bluepay_obj = False


class WebsiteSale(WebsiteSale):

    @http.route(['/get_bluepay_data'], type='json', auth="public", website=True)
    def get_bluepay_data(self, **kw):
        global bluepay_obj
        bluepay_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'bluepay')], limit=1)
        payment_transaction = request.env['payment.transaction'].sudo().search([], limit=1)
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return_url = base_url + '/shop/completeCallback'
        decline_url = base_url + '/shop/completeCallback'
        account_details = BluePay(
            account_id = bluepay_id.account_id, 
            secret_key = bluepay_id.bluepay_secret_key, 
            mode = bluepay_id.state 
            )
        bluepay_obj = account_details
        generated_url = account_details.generate_url(
            merchant_name = bluepay_id.merchant_name,
            transaction_type = 'SALE',
            accept_discover = 'Yes',
            accept_amex = 'Yes',
            amount =  str(payment_transaction.amount),
            protect_amount = 'No',
            rebilling = 'Yes',
            reb_protect = 'No',
            reb_amount = '50',
            reb_cycles = '12',
            reb_start_date = '1 MONTH',
            reb_frequency = '1 MONTH',
            protect_custom_id = 'No',
            custom_id2 = '15',
            protect_custom_id2 = 'No',
            payment_template = 'mobileform01',
            receipt_temp_remote_url='',
            receipt_template = 'defaultres1',
            return_url = return_url
            )
        params = {
            'NAME1' : payment_transaction.partner_id.name or '',
            'NAME2': payment_transaction.partner_id.name or '',
            'ADDR1': payment_transaction.partner_id.street or '',
            'ADDR2': payment_transaction.partner_id.street2 or '',
            'CITY':  payment_transaction.partner_id.city or '',
            'STATE': payment_transaction.partner_id.state_id.name or '',
            'ZIPCODE': payment_transaction.partner_id.zip or '',
            'COUNTRY': payment_transaction.partner_id.country_id.name or '',
            'EMAIL': payment_transaction.partner_id.email or '',
            'PHONE': payment_transaction.partner_id.phone or ''
                }
        response = requests.get(generated_url,
                    params=params)
        data = str(response.url).split('&')
        # print("\n\n\n******************",json.dumps(str(data)))
        test_str = response.url
        # print("\n\n\n\nURLLLLLLLLLLLL", test_str, "\n\n\n")
        # request.httprequest.session.test_str = json.dumps(test_str)
        request.httprequest.session.data = data
        1/0
        return test_str
        # for_url = {
        #     'SHPF_FORM_ID':'mobileform01',
        #     'SHPF_ACCOUNT_ID':bluepay_id.account_id,
        #     'SHPF_TPS_DEF':'SHPF_FORM_ID SHPF_ACCOUNT_ID DBA TAMPER_PROOF_SEAL AMEX_IMAGE DISCOVER_IMAGE TPS_DEF TPS_HASH_TYPE SHPF_TPS_DEF SHPF_TPS_HASH_TYPE',
        #     'SHPF_TPS_HASH_TYPE':'HMAC_SHA512',
        #     'SHPF_TPS': bluepay_id.bluepay_secret_key,
        #     'MODE':bluepay_id.state,
        #     'TRANSACTION_TYPE':'SALE',
        #     'DBA':bluepay_id.merchant_name,
        #     'AMOUNT': str(payment_transaction.amount),
        #     'TAMPER_PROOF_SEAL': '',
        #     'REBILLING':'Yes',
        #     'AMEX_IMAGE':'Yes',
        #     'DISCOVER_IMAGE':'Yes',
        #     'protect_amount':'Yes',
        #     'rebilling':'Yes',
        #     'receipt_template':'defaultres1',
        # }
        # print("\n\n\n\n\nURLLLLLLLL",for_url)
        # bluepay_form_url = 'https://secure.bluepay.com/interfaces/shpf?'
        # f = requests.post(bluepay_form_url, data=for_url)
        # data = str(f.content).split('&')
        # print("\n\n\n\n\nkkkkkkkkkkkk", data)
        # data = str(response.content).split('&')
        # print("\n\n\n\n\n\nBBBBBBBBBBBBB",data)
        # 5/0
        # main_url = response.url
        # else:
        #     generated_url = account_details.generate_url(
        #         merchant_name = bluepay_id.merchant_name,
        #         transaction_type = 'SALE',
        #         accept_discover = 'Yes',
        #         accept_amex = 'Yes',
        #         amount =  str(payment_transaction.amount),
        #         protect_amount = 'Yes',
        #         rebilling = 'Yes',
        #         reb_protect = 'Yes',
        #         reb_amount = '50',
        #         reb_cycles = '12',
        #         reb_start_date = '1 MONTH',
        #         reb_frequency = '1 MONTH',
        #         custom_id = '',
        #         protect_custom_id = 'Yes',
        #         custom_id2 = '15',
        #         protect_custom_id2 = 'Yes',
        #         payment_template = 'mobileform01',
        #         receipt_template = 'defaultres1',
        #         receipt_temp_remote_url = '',
        #         return_url = decline_url
        #         )
        #     params = {'NAME1' : payment_transaction.partner_id.name or '',
        #             'NAME2': payment_transaction.partner_id.name or '',
        #             'ADDR1': payment_transaction.partner_id.street or '',
        #             'ADDR2': payment_transaction.partner_id.street2 or '',
        #             'CITY':  payment_transaction.partner_id.city or '',
        #             'STATE': payment_transaction.partner_id.state_id.name or '',
        #             'ZIPCODE': payment_transaction.partner_id.zip or '',
        #             'COUNTRY': payment_transaction.partner_id.country_id.name or '',
        #             'EMAIL': payment_transaction.partner_id.email or '',
        #             'PHONE': payment_transaction.partner_id.phone or ''}
        #     response = requests.get(generated_url,
        #                 params=params)
        #     print("\n\n\n\n\n\n\n RESPONSE:-",response)
        #     main_url = response.url
        #     print("\n\n\n\n\n KWWWWW222222222:--", kw)
        #     return main_url
            # payment_acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', 'bluepay')])
            # payment_token = request.env['payment.token'].sudo().search([('acquirer_id', '=', payment_acquirer.id)])
            # sale_order_id = request.session.get('sale_last_order_id')
            # if sale_order_id:
            #     order = request.env['sale.order'].sudo().browse(sale_order_id)
            #     payment_transaction = request.env['payment.transaction'].sudo().search([], limit=1)
            #     payment_transaction._process_feedback_data(post)
            #     return request.redirect('/shop/confirmation')
            # else:
            #     return request.redirect('/shop') 

    @http.route(['/shop/completeCallback'], type='http', auth="public", website=True)
    def confirm_order_new(self, **post):
        print("\n\n\n\n\n----POSTT---",post)
        # test_url = json.loads(request.httprequest.session.test_str)
        test_url = request.httprequest.session.data
        print("\n\n\n\n>>>request.httprequest.session.final_data>>",test_url)
        for item in test_url:
            print(">>>>",test_url.status_response)
        payment_transaction = request.env['payment.transaction'].sudo().search([], limit=1)
        payment_transaction._process_feedback_data(post)
        print("\n\n\n\n>>>>>>> SHOPP",request.redirect('/shop/confirmation'))
        print ("\n bluepay_obj >>>>>>>>. ",bluepay_obj)
        # print ("\n bluepay_obj >>>>>>>>. ",self._context)
        # print ("\n bluepay_obj >>>>>>>>. ",bluepay_obj.account_id)
        # bluepay_obj.set_customer_information(
        #     name1 = payment_transaction.partner_id.name or '',
        #     name2 = payment_transaction.partner_id.name or '',
        #     addr1 = payment_transaction.partner_id.street or '',
        #     addr2 = payment_transaction.partner_id.street2 or '',
        #     city = payment_transaction.partner_id.city or '',
        #     state = payment_transaction.partner_id.state_id.name or '',
        #     zipcode = payment_transaction.partner_id.zip or '',
        #     country = payment_transaction.partner_id.country_id.name or '',
        # )
        # bluepay_obj.set_cc_information(
        #     card_number = "4111111111111111",
        #     card_expire = "1225",
        #     cvv2 = "123"
        # )

        # bluepay_obj.auth(amount = str(payment_transaction.amount))
        # bluepay_obj.process()

        # # Reads the response from BluePay
        # demo = bluepay_obj.response
        # print("\n\n\n\n\nAFTER transaction:>>>>>>",demo)
        # # print ("\n bluepay_obj RESPONSE>>>>>>>>. ",bluepay_obj.status_response)
        5/0
        return request.redirect('/shop/confirmation')
    
    # @http.route(['/shop'], type='http', auth="public", website=True)
    # def confirm_order_new_decline(self, **post):
    #     print("\n\n\n\n\n----POSTT--",post)
    #     print("\n\n\n\n>>>REQUEST>>",request.session)
    #     print("\n\n\n\n>>>REQUEST>>",self)
    #     # print("\n\n\n\n>>>REQUEST>>",self._context)
    #     payment_transaction = request.env['payment.transaction'].sudo().search([], limit=1)
    #     payment_transaction._process_feedback_data(post)
    #     print("\n\n\n\n>>>>>>>SHOPP",request.redirect('/shop/confirmation'))
    #     return request.redirect('/shop/confirmation')   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
