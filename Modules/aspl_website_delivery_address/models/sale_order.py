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

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_address(self, line_id):
        order_line = self.env['sale.order.line']
        if line_id:
            order_line = self.env['sale.order.line'].sudo().browse(int(line_id))
        partner_id = self.env.user.partner_id
        delivery_address = list(partner_id and partner_id.child_ids.filtered(lambda l: l.type == 'delivery'))
        delivery_address.append(partner_id)
        data = []
        for each in delivery_address:
            if order_line and order_line.shipping_id.id == each.id:
                data.append({'id': each.id, 'name': each.name.title(), 'street': each.street if each.street else '',
                             'street2': each.street2 if each.street2 else '', 'zip': each.zip if each.zip else '',
                             'email': each.email if each.email else '', 'selected': True})
            else:
                data.append({'id': each.id, 'name': each.name.title(), 'street': each.street if each.street else '',
                             'street2': each.street2 if each.street2 else '', 'zip': each.zip if each.zip else '',
                             'email': each.email if each.email else '', 'selected': False})
        return data


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shipping_id = fields.Many2one('res.partner', string='Shipping Address')

    def add_delivery_address(self, add_id):
        if add_id:
            self.sudo().write({'shipping_id': int(add_id)})

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        res.update({
            'partner_id': self.shipping_id.id if self.shipping_id else self.order_id.partner_shipping_id.id
        })
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrderLine, self).create(vals_list)
        res.shipping_id = res.order_id.partner_shipping_id.id
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
