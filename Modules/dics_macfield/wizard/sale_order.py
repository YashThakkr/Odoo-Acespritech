# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ServiceProductWizard(models.TransientModel):
    _name = 'service.product.wizard'
    _description = 'Show Discount Product'

    product_id = fields.Many2one('product.product', string="Discount Product", required=True)
    price_unit = fields.Float(string="Unit Price", required=True, )

    def button_confirm(self):
        sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
        sale_order_line = self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product_id.id,
            'price_unit': -abs(self.price_unit),
        })
        return {
            'type': 'ir.actions.act_window_close',
        }
