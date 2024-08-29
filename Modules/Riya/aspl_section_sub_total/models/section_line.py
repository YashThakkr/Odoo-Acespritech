# -*- coding: utf-8 -*-
##############################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
##############################################################################
from odoo import models, fields


class SectionLine(models.Model):
	_name = 'section.line'
	_description = 'Section Line'

	section_name = fields.Char('Section')
	total = fields.Monetary('Total')
	sale_order_id = fields.Many2one('sale.order', string="Sales Order")
	purchase_order_id = fields.Many2one(
		'purchase.order', string="Purchase Order")
	currency_id = fields.Many2one('res.currency', string='Currency')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
