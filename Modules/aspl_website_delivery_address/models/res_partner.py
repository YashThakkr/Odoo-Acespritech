# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t   it and/or modify it.
#
#################################################################################

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def create_address(self, name, street, street2, zip, city, state, country, phone, email):
        delivery_add = self.sudo().create({'type': 'delivery',
                                           'name': str(name),
                                           'street': str(street),
                                           'street2': str(street2),
                                           'zip': str(zip),
                                           'city': city,
                                           'state_id': int(state),
                                           'country_id': int(country),
                                           'phone': str(phone),
                                           'email': str(email),
                                           'parent_id': int(self.env.user.partner_id.id)})
        return delivery_add.id

    def check_used_address(self, add_id):
        order_ids = self.env['sale.order'].sudo().search([('partner_id', '=', self.env.user.partner_id.id)])
        order_lines = self.env['sale.order.line'].sudo().search([('order_partner_id', '=', self.env.user.partner_id.id)])
        if add_id in order_ids.mapped('partner_shipping_id').ids or add_id == self.env.user.partner_id.id\
                or add_id in order_lines.mapped('shipping_id').ids:
            return True
        else:
            return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
