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

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    @http.route(['/get-product-list'], type='json', auth="public", website=True)
    def get_product_list(self, search_string='', **post):
        res = request.env['product.product'].search(['|', ('name', 'ilike', str(search_string)),
                                                     ('default_code', 'ilike', str(search_string)),
                                                     ('product_tmpl_id.website_published', '=', True)])
        product_list = []
        for each in res:
            tax_total = 0
            for tax in each.taxes_id:
                tax = tax.compute_all(each.list_price, request.website.currency_id, 1, product=each)
                for tax_amount in tax['taxes']:
                    tax_total += tax_amount['amount']

            product_list.append(
                {'list_price': each.list_price, 'id': each.id, 'currency': request.website.currency_id.symbol,
                 'tax_total': tax_total, 'name': each.display_name})
        return product_list
    
    @http.route(['/get-cuurency-symbol'], type='json', auth="public", website=True)
    def get_symbol_cuurency(self, **post):
        print('request.website.currency_id.symbol',request.website.currency_id.symbol)
        return [{'currency': request.website.currency_id.symbol}]

    @http.route(['/listcart/update'], type='json', methods=['POST'], website=True, auth="public")
    def cart_update_list(self, product_list, **kw):
        if product_list:
            for product in product_list:
                if product.get('product_id') and product.get('qty'):
                    request.website.sale_get_order(force_create=1)._cart_update(
                        product_id=int(product['product_id']),
                        add_qty=float(product['qty']),
                        set_qty=0,
                    )
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
