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

from odoo import fields, models, api, _


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    fast_order_qty = fields.Integer(string="Fast Order Default Quantity")

    @api.model
    def get_values(self):
        res = super(ResConfig, self).get_values()
        param_obj = self.env['ir.config_parameter']
        res.update({
            'fast_order_qty': int(
                param_obj.sudo().get_param('aspl_website_fast_order.fast_order_qty')),
        })
        return res

    def set_values(self):
        res = super(ResConfig, self).set_values()
        param_obj = self.env['ir.config_parameter']
        param_obj.sudo().set_param('aspl_website_fast_order.fast_order_qty', self.fast_order_qty)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
