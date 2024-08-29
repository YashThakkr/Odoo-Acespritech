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

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    total_discount = fields.Float(string="Total Discount", readonly=True)
    sale_vouchercode = fields.Many2one('gift.voucher.detail', string="Sale Promocode")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


