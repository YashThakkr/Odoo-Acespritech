# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductChangeQuantity(models.TransientModel):
	_inherit = "stock.change.product.qty"

	# update inventory line when update stock by "Update Qty On Hand" button from product.
	def _action_start_line(self):
		line_data=super(ProductChangeQuantity, self)._action_start_line()
		for rec in self:
			secondary_qty = 0.0
			if rec.product_id.secondary_uom_id.uom_type =='bigger':
				if rec.product_id.secondary_uom_id.factor_inv != 0:
					secondary_qty = line_data['product_qty']/rec.product_id.secondary_uom_id.factor_inv
			if rec.product_id.secondary_uom_id.uom_type =='smaller':
				secondary_qty = line_data['product_qty'] * rec.product_id.secondary_uom_id.factor
			line_data.update({'secondary_uom_id':rec.product_id.secondary_uom_id.id, 'secondary_quantity':secondary_qty})
		return line_data
