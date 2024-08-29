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

from odoo import models, fields, api, _


class AcesSmallBarcodeLabelLine(models.TransientModel):
    _name = 'aces.small.barcode.label.line'

    font_size = fields.Integer(string="Font Size", default=10)
    font_color = fields.Selection([('black', 'Black'), ('blue', 'Blue'),
                                   ('cyan', 'Cyan'), ('gray', 'Gray'),
                                   ('green', 'Green'), ('lime', 'Lime'),
                                   ('maroon', 'Maroon'), ('pink', 'Pink'),
                                   ('purple', 'Purple'), ('red', 'Red'),
                                   ('yellow', 'Yellow')], string="Font Color", default='black')
    sequence = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], string="Sequence")
    name = fields.Selection([('default_code', 'Internal Reference'),
                             ('name', 'Product Name'),
                             ('lst_price', 'Sale Price'),
                             ('barcode', 'Barcode'),
                             ('image_1920', 'Product Image')], string="Name")
    barcode_label_id = fields.Many2one('aces.small.barcode.label', string="Barcode Label ID")


class AcesSmallBarcodeLabelLine(models.TransientModel):
    _name = 'aces.small.product.label.qty'

    product_id = fields.Many2one('product.product', string="Product(s)", required=True)
    qty = fields.Integer(string="Quantity", default=1)
    barcode_label_id = fields.Many2one('aces.small.barcode.label', string="Barcode Label ID")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
