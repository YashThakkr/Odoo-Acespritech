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
import random
from datetime import date

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo import http
from odoo import fields
from odoo.tools.json import scriptsafe as json_scriptsafe


class GiftVoucher(WebsiteSale):
    @http.route(['/discount_cancel'], type='json', auth="public", website=True)
    def discount_cancel(self, discount, **post):
        if discount:
            dis_amount = discount.split(' ')
            sale_order_detail_id1 = request.env['sale.order'].sudo().browse(request.session['sale_order_id'])
            if sale_order_detail_id1.sale_vouchercode:
                product_id = int(
                    request.env['ir.config_parameter'].sudo().get_param('aspl_website_gift_voucher.product_id'))
                record = request.env['sale.order.line'].sudo().search(
                    [('order_id', '=', sale_order_detail_id1.id), ('product_id', '=', product_id)])
                record.sudo().unlink()
                sale_order_detail_id1.sale_vouchercode = None
                sale_order_detail_id1.total_discount = 0.0
                sale_order_detail_id1.amount_total = sale_order_detail_id1.amount_untaxed
            return True

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))
        order_id = request.website.sale_get_order(force_create=1)
        # voucher_product_id = int(self.env['ir.config_parameter'].sudo().get_param('aspl_website_gift_voucher.product_id'))
        order_id._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values
        )
        return request.redirect("/shop/cart")

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def shop_payment_confirmation(self, **post):
        payment_confirm = super(GiftVoucher, self).shop_payment_confirmation(post=post)
        sale_order_id = request.session.get('sale_last_order_id')
        sale_order_detail_voucher = request.env['sale.order'].browse(sale_order_id)
        voucher_detail = request.env['gift.voucher.detail'].search([('id', '=', sale_order_detail_voucher.sale_vouchercode.id)])
        if sale_order_detail_voucher.sale_vouchercode:
            voucher_detail.write({'redeem_voucher_ids':[(0, 0, {'customer_id': request.env.user.id,
                                                                'used_date': date.today(),
                                                                'voucher_code': sale_order_detail_voucher.sale_vouchercode.code,
                                                                'order_amount': sale_order_detail_voucher.amount_untaxed,
                                                                'voucher_amount': sale_order_detail_voucher.total_discount,
                                                                'order_name': sale_order_detail_voucher.name})]})
        return payment_confirm

    def discount_count(self, voucher, sale_order, discount_total, cnt_tot):
        sale_order_detail_id = request.env['sale.order'].sudo().browse(request.session['sale_order_id'])

        if voucher.discount_type == 'percentage':
            product_id = int(
                request.env['ir.config_parameter'].sudo().get_param('aspl_website_gift_voucher.product_id'))
            if not product_id:
                raise ValidationError('Please configure Gift Voucher Product')
            data = [(0, 0, {
                'product_id': product_id,
                'product_uom_qty': 1,
                'price_unit': float(-1 * discount_total * voucher.discount / 100) if voucher.voucher_type == 'category' 
                              else float(-1 * sale_order_detail_id.amount_untaxed * voucher.discount / 100),
            })]
            record = sale_order_detail_id.sudo().write({
                'order_line': data,
                'total_discount': discount_total * voucher.discount / 100 if voucher.voucher_type == 'category' 
                                  else sale_order_detail_id.amount_untaxed * voucher.discount / 100,
                'sale_vouchercode': voucher.id
            })
        elif voucher.discount_type == 'fixed':
            product_id = int(
                request.env['ir.config_parameter'].sudo().get_param('aspl_website_gift_voucher.product_id'))
            if not product_id:
                raise ValidationError('Please configure Gift Voucher Product')
            data = [(0, 0, {
                'product_id': product_id,
                'product_uom_qty': 1,
                'price_unit': float(-1 * voucher.discount),
            })]
            record = sale_order_detail_id.sudo().write({
                'order_line': data,
                'total_discount': voucher.discount,
                'sale_vouchercode': voucher.id,
            })
        return True

    @http.route(['/discount_cart'], type='json', auth="public", website=True)
    def discount_cart(self, code, **post):
        current_date = date.today()
        if code:
            sum_qty, count_total, total = 0, 0, 0
            voucher_detail_search = request.env['gift.voucher.detail'].search([('code', '=', code)])
            voucher_detail = request.env['gift.voucher.detail'].search([('code', '=', code), ('expiry_date', '>=',
                                                                                              str(current_date))])
            if not voucher_detail_search:
                return {'code': 'Not valid voucher code'}
            sale_order_detail_id = request.env['sale.order'].sudo().browse(request.session['sale_order_id'])
            if voucher_detail and str(voucher_detail.expiry_date) >= str(current_date):
                sale_order_redeeption_count = request.env['sale.order'].search_count([('partner_id', '=',
                                                                                       request.env.user.partner_id.id),
                                                                                      ('sale_vouchercode', '=',
                                                                                       voucher_detail.id)])
                if sale_order_detail_id.amount_total < voucher_detail.discount:
                    return {'code': 'Voucher discount greter then total amount'}
                if voucher_detail.redemption_customer > sale_order_redeeption_count:
                    for each1 in sale_order_detail_id.order_line:
                        sum_qty += each1.product_uom_qty
                    total = sale_order_detail_id.amount_untaxed
                    if voucher_detail.voucher_type == 'order_total':
                        if total >= voucher_detail.minimum_amount:
                            return self.discount_count(voucher_detail, sale_order_detail_id, total, count_total)
                        else:
                            return {'code': 'Order total amount is low to voucher limit'}
                    elif voucher_detail.voucher_type == 'category':
                        child_cate = request.env['ir.config_parameter'].sudo().get_param(
                            'aspl_website_gift_voucher.child_cate')
                        if not child_cate:
                            toal_amount_count = 0
                            for order_cate in sale_order_detail_id.order_line:
                                for category_in_voucher in voucher_detail.category_type.ids:
                                    if category_in_voucher in order_cate.product_id.public_categ_ids.ids:
                                        toal_amount_count += order_cate.price_subtotal
                                        break
                            if toal_amount_count:
                                return self.discount_count(voucher_detail, sale_order_detail_id, toal_amount_count, count_total)
                            else:
                                return {'code': 'Category not match'}
                        else:
                            amount_to_calculate = 0
                            for line in sale_order_detail_id.order_line:
                                for category in line.product_id.public_categ_ids:
                                    if category.id in voucher_detail.category_type.ids:
                                        amount_to_calculate += line.price_subtotal
                                    else:
                                        check_parent = self.checkparent(category, voucher_detail.category_type)
                                        if check_parent:
                                            amount_to_calculate += line.price_subtotal
                            if amount_to_calculate:
                                return self.discount_count(voucher_detail, sale_order_detail_id, amount_to_calculate,
                                                           count_total)
                            else:
                                return {'code': 'Category not match'}
                    return True
                else:
                    return {'code': 'Voucher redeeption zero'}
            else:
                return {'code': 'Expired your voucher'}
        else:
            return {'code': 'Please enter voucher code'}

    def checkparent(self, cat_id, voucher_detail):
        if cat_id.parent_id.id in voucher_detail.ids:
            return True
        elif cat_id.parent_id.parent_id:
            self.checkparent(cat_id.parent_id, voucher_detail)
        else:
            return False

    @http.route(['/notification'], type='json', auth="public", website=True)
    def check_notification(self, **post):
        notifications = request.env['res.config.settings'].sudo().search([], limit=1, order='id desc')
        if notifications.voucher_show_option == 'notification':
            delaytime = notifications.delay_time
            if notifications.voucher_notification_show == 'pageload':
                return {'detail': 'pageload',
                        'delaytime': delaytime}
            elif notifications.voucher_notification_show == 'intervaltime':
                minute = notifications.interval_time
                return {'detail': 'intervaltime',
                                   'minute': minute,
                                    'delaytime': delaytime}

    @http.route(['/shownotification'], type='json', auth="public", website=True)
    def show_notification(self, **post):
        voucher_enable = request.env['ir.config_parameter'].sudo().get_param('aspl_website_gift_voucher.gift_voucher')
        if voucher_enable:
            list = []
            data = request.env['gift.voucher.detail'].search([]).read()
            while True:
                random_selected = random.SystemRandom().choice(data)
                if str(random_selected['expiry_date']) >= str(date.today()):
                    if random_selected['voucher_type'] == 'category':
                        for type in random_selected['category_type']:
                            categ_type = request.env['product.public.category'].browse(type)
                            for categ in categ_type:
                                list.append(categ.name)

                        if random_selected['discount_type'] == 'fixed':
                            message = "Flat <b>  "+str(random_selected['discount'])+"   Rs.</b> " +" off on  <br>"+"<b>"+ ', '.join(list)+" </b>  Products. <br> <br> <style='margin-left:40px;'> Use Code:-  "+"<b id='copy-code-detail'>"+random_selected['code']+"</b>"
                            return {'message': message}

                        else:
                            message = "Flat <b>  "+str(random_selected['discount'])+"   % </b> " +" off on  <br>"+"<b>"+ ', '.join(list)+" </b>  Products. <br> <br> <style='margin-left:40px;'> Use Code:-  "+"<b id='copy-code-detail'>"+random_selected['code']+"</b>"
                            return {'message': message}

                    else:

                        if random_selected['discount_type'] == 'fixed':
                            message = "Flat <b>  "+str(random_selected['discount'])+"   Rs. </b> " +" off on  <br> Total order Of "+"<b>"+str(random_selected['minimum_amount']) + " Rs.<br> <br> <style='margin-left:40px;'> Use Code:-  "+"<b id='copy-code-detail'>"+random_selected['code']+"</b>"
                            return {'message': message}

                        else:
                            message = "Flat <b>  "+str(random_selected['discount'])+"   % </b> " +" off on  <br> Total order Of "+"<b>"+str(random_selected['minimum_amount']) + " Rs.<br> <br> <style='margin-left:40px;'> Use Code:-  "+"<b id='copy-code-detail'>"+random_selected['code'] + "</b>"
                            return {'message': message}

    @http.route(['/voucher'], type='http', auth='public', website=True)
    def voucher_details_page(self, **kwargs):
        val = {
            'voucher_data': request.env['gift.voucher.detail'].search([])
        }
        return request.render("aspl_website_gift_voucher.voucher_detail_template", val)

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kw):
        """
        This route is called :
            - When changing quantity from the cart.
            - When adding a product from the wishlist.
            - When adding a product to cart on the same page (without redirection).
        """
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            if kw.get('force_create'):
                order = request.website.sale_get_order(force_create=1)
            else:
                return {}

        pcav = kw.get('product_custom_attribute_values')
        nvav = kw.get('no_variant_attribute_values')
        voucher_product_id = int(
            request.env['ir.config_parameter'].sudo().get_param('aspl_website_gift_voucher.product_id'))
        if order.sale_vouchercode:
            for line in order.order_line:
                if line.product_id.id == voucher_product_id:
                    order.sale_vouchercode = None
                    order.total_discount = 0.0
                    line.sudo().unlink()
        value = order._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=json_scriptsafe.loads(pcav) if pcav else None,
            no_variant_attribute_values=json_scriptsafe.loads(nvav) if nvav else None
        )

        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity

        if not display:
            return value

        value['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view']._render_template(
            "website_sale.short_cart_summary", {
                'website_sale_order': order,
            })
        return value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
