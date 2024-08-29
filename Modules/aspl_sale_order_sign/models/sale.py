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
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from lxml import etree

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter']
        res.update({'signature': param_obj.sudo().get_param('aspl_sale_order_sign.signature')})
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param_obj = self.env['ir.config_parameter']
        param_obj.sudo().set_param('aspl_sale_order_sign.signature', self.signature)

    signature = fields.Boolean("Require Signature")
    


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    signature = fields.Binary(string="Signature")
    
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        config_sign = self.env['ir.config_parameter'].sudo().get_param('aspl_sale_order_sign.signature')
        if config_sign and (not self.signature):
            raise UserError(_('Signature is required to confirm sale order.'))
        else:
            return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: