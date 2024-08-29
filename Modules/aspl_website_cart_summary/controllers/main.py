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


from odoo import fields, http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.addons.payment import utils as payment_utils


class CartSummary(http.Controller):
    @http.route('/shop/cart_summary', auth='public', type='json', website=True)
    def cart_summary(self, **kw):
        browse_rec = request.env['sale.order.line'].sudo().browse(int(kw.get('line_id'))).unlink()
        return {'data': request.env['ir.ui.view']._render_template("aspl_website_cart_summary.website_cart_summary")}


class WebsiteCartSummary(WebsiteSale):
    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(
            self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
            product_custom_attribute_values=None, no_variant_attribute_values=None, **kw
    ):
        """
        This route is called :
            - When changing quantity from the cart.
            - When adding a product from the wishlist.
            - When adding a product to cart on the same page (without redirection).
        """
        order = request.website.sale_get_order(force_create=True)
        if order.state != 'draft':
            request.website.sale_reset()
            if kw.get('force_create'):
                order = request.website.sale_get_order(force_create=True)
            else:
                return {}

        if product_custom_attribute_values:
            product_custom_attribute_values = json_scriptsafe.loads(product_custom_attribute_values)

        if no_variant_attribute_values:
            no_variant_attribute_values = json_scriptsafe.loads(no_variant_attribute_values)

        values = order._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
            **kw
        )

        values['notification_info'] = self._get_cart_notification_information(order, [values['line_id']])
        values['notification_info']['warning'] = values.pop('warning', '')
        request.session['website_sale_cart_quantity'] = order.cart_quantity

        if not order.cart_quantity:
            request.website.sale_reset()
            return values

        values['cart_quantity'] = order.cart_quantity
        values['minor_amount'] = payment_utils.to_minor_currency_units(
            order.amount_total, order.currency_id
        ),
        values['amount'] = order.amount_total

        if not display:
            return values

        values['cart_ready'] = order._is_cart_ready()
        values['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template(
            "website_sale.cart_lines", {
                'website_sale_order': order,
                'date': fields.Date.today(),
                'suggested_products': order._cart_accessories()
            }
        )
        values['website_sale.total'] = request.env['ir.ui.view']._render_template(
            "website_sale.total", {
                'website_sale_order': order,
            }
        )
        values['cart_summary'] = request.env['ir.ui.view']._render_template(
            "aspl_website_cart_summary.website_cart_summary", {
                'website_sale_order': order,
            })
        return values
    # def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kw):
    #     """This route is called when changing quantity from the cart or adding
    #     a product from the wishlist."""
    #     order = request.website.sale_get_order(force_create=1)
    #     if order.state != 'draft':
    #         request.website.sale_reset()
    #         return {}
    #
    #     value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kw)
    #     if not order.cart_quantity:
    #         request.website.sale_reset()
    #         return value
    #
    #     order = request.website.sale_get_order()
    #     value['cart_quantity'] = order.cart_quantity
    #
    #     if not display:
    #         return value
    #
    #     value['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template("website_sale.cart_lines", {
    #         'website_sale_order': order,
    #         'date': fields.Date.today(),
    #         'suggested_products': order._cart_accessories()
    #     })
    #     value['website_sale.total'] = request.env['ir.ui.view']._render_template(
    #         "website_sale.total", {
    #             'website_sale_order': order,
    #         })
    #     value['cart_summary'] = request.env['ir.ui.view']._render_template(
    #         "aspl_website_cart_summary.website_cart_summary", {
    #             'website_sale_order': order,
    #         })
    #     return value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
