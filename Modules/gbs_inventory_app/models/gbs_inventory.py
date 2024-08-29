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

from odoo import fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    hide_price = fields.Boolean(string='Hide Price', groups='gbs_inventory_app.group_hide_price')
    show_price = fields.Boolean(string='Show Price', groups='gbs_inventory_app.group_show_price')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_product = fields.Boolean(string='Is Product', help='Indicates if this is a product')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    signature = fields.Binary(string='Signature')

    in_transit = fields.Boolean(string='In Transit', help='Indicates if the shipment is currently in transit')
    transit_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled')
    ], string='Transit Status', default='pending')
    expected_delivery_date = fields.Date(string='Expected Delivery Date')
    current_location = fields.Char(string='Current Location')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: