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

import os
import re

import xlrd
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import operator

dir_path = os.path.dirname(os.path.realpath(__file__))


class WebsiteSale(WebsiteSale):

    @http.route(['/fast_order'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def fast_order(self, **post):
        """This method is used to product code,product quantity to display in add to cart."""
        param_obj = request.env['ir.config_parameter']
        default_qty = int(param_obj.sudo().get_param('aspl_website_fast_order_ee.fast_order_qty'))
        if post.get('text'):
            product_list = post.get('text').split('\r\n')
            for each in product_list:
                if each and ',' in each:
                    product_data = re.sub(r"\s", "", each).split(',')
                    product_code = product_data[0]
                    if product_code != '':
                        if product_data[1] and int(product_data[1]) == 0 or not product_data[1]:
                            qty = default_qty
                        else:
                            qty = int(product_data[1])
                        product = request.env['product.product'].sudo().search(
                            [('default_code', 'ilike', str(product_code))], limit=1)
                        if product:
                            request.website.sale_get_order(force_create=1)._cart_update(
                                product_id=product.id,
                                add_qty=int(qty) or 1,
                                set_qty=0,
                            )
                else:
                    product_code = each
                    qty = default_qty
                    product = request.env['product.product'].sudo().search(
                        [('default_code', 'ilike', str(product_code))])
                    if product:
                        request.website.sale_get_order(force_create=1)._cart_update(
                            product_id=product.id,
                            add_qty=int(qty) or 1,
                            set_qty=0,
                        )
            return request.redirect('/shop/cart')
        if post.get('file_type'):
            if post.get('file_type') == 'csv':
                file = (post.get('csv_file').read()).decode("utf-8").splitlines()
                for each in file:
                    if each:
                        product_data = re.sub(r"\s", "", each).split(',')
                        product_code = product_data[0]
                        if product_code != '':
                            if len(product_data) > 1:
                                if product_data[1] and int(product_data[1]) == 0 or product_data[1] == '':
                                    qty = default_qty
                                else:
                                    qty = product_data[1]
                            else:
                                qty = default_qty
                            product = request.env['product.product'].sudo().search(
                                [('default_code', 'ilike', str(product_code))], limit=1)
                            if product:
                                request.website.sale_get_order(force_create=1)._cart_update(
                                    product_id=product.id,
                                    add_qty=int(qty) or 1,
                                    set_qty=0,
                                )
                return request.redirect('/shop/cart')
            else:
                file = post.get('xls_file').save(os.path.join(dir_path, post.get('xls_file').filename))
                workbook = xlrd.open_workbook(os.path.join(dir_path, post.get('xls_file').filename))
                for sheetName in workbook.sheet_names():
                    sheet = workbook.sheet_by_name(sheetName)
                    for row_no in range(sheet.nrows):
                        product_code = str(((sheet.cell(row_no, 0)).value)).strip(" .0")
                        if product_code:
                            if sheet.ncols > 1 and (sheet.cell(row_no, 1)).value != 0 and (sheet.cell(row_no, 1)).value != '':
                                qty = (sheet.cell(row_no, 1)).value
                            else:
                                qty = default_qty
                            product = request.env['product.product'].sudo().search(
                                [('default_code', 'ilike', str(product_code))], limit=1)
                            if product:
                                request.website.sale_get_order(force_create=1)._cart_update(
                                    product_id=product.id,
                                    add_qty=int(qty) or 1,
                                    set_qty=0,
                                )
                os.remove(os.path.join(dir_path, post.get('xls_file').filename))
                return request.redirect('/shop/cart')
        product_dict = {}
        record_set = request.env['sale.order'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id), ('state', '=', 'sale')])
        for record in record_set:
            for product_template in record.order_line:
                if not product_dict:
                    product_dict[product_template.product_template_id.product_variant_id.id] = product_template.product_uom_qty
                else:
                    if product_template.product_template_id.product_variant_id.id in list(product_dict.keys()):
                        product_dict[product_template.product_template_id.product_variant_id.id] = product_dict[product_template.product_template_id.product_variant_id.id] + product_template.product_uom_qty
                    else:
                        product_dict[product_template.product_template_id.product_variant_id.id] = product_template.product_uom_qty
        sorted_d = dict(sorted(product_dict.items(), key=operator.itemgetter(1), reverse=True))
        product_dict.clear()
        list_record = list(sorted_d.keys())
        for each in range(0, 10):
            if each < len(list_record):
                product_dict[list_record[each]] = int(sorted_d[list_record[each]])
        return request.render('aspl_website_fast_order_ee.fast_order', {'product_dict': product_dict})

    @http.route(['/get-product-list'], type='json', auth="public", website=True)
    def get_product_list(self, search_string='', **post):
        res = request.env['product.product'].sudo().search([('product_tmpl_id.website_published', '=', True)])
        product_list = []
        for each in res:
            tax_total = 0
            for tax in each.taxes_id:
                tax = tax.compute_all(each.lst_price, request.website.currency_id, 1, product=each)
                for tax_amount in tax['taxes']:
                    tax_total += tax_amount['amount']

            product_list.append(
                {'list_price': each.lst_price, 'id': each.id, 'currency': request.website.currency_id.symbol,
                 'tax_total': tax_total, 'name': each.display_name, 'image': each.image_1920})
        return product_list

    @http.route(['/listcart/update'], type='json', methods=['POST'], website=True, auth="public")
    def cart_update_list(self, product_list, **kw):
        if product_list:
            for product in product_list:
                if product['product_id'] and product['qty']:
                    value = request.website.sale_get_order(force_create=1)._cart_update(
                        product_id=int(product['product_id']),
                        add_qty=float(product['qty']),
                        set_qty=0,
                    )
        return value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
