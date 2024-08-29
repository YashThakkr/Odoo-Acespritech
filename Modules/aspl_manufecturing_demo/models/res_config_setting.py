# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#################################################################################
from odoo import models, fields, api


class WebsiteConfig(models.TransientModel):
    _inherit = "res.config.settings"

    website_gift_card = fields.Boolean(string="Gift Card", config_parameter='aspl_website_gift_card_ee.website_gift_card')
    product_id = fields.Many2one('product.product', string='Gift Card Product', config_parameter='aspl_website_gift_card_ee.product_id', domain=[('type', '=', 'service')])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: