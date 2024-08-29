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
from odoo.exceptions import UserError


class AcesSmallBarcodeTemplate(models.Model):
    _name = 'aces.small.barcode.template'

    def close_wizard(self):
        self.write({'active': False})
        return {
            'name': _('Product Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'aces.small.barcode.label',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }

    def go_to_label_wizard(self):
        ''' when u save Product Label Template then u'll return on Dynamic Product Label page'''

        if not self.name:
            raise UserError(_('Template Design Name is required.'))
        return {
            'name': _('Product Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'aces.small.barcode.label',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }

    @api.model
    def default_get(self, fields_list):
        res = super(AcesSmallBarcodeTemplate, self).default_get(fields_list)
        if self._context.get('wiz_id') and self._context.get('from_wizard'):
            for wiz in self.env['aces.small.barcode.label'].browse(self._context.get('wiz_id')):
                prod_list = []
                for line in wiz.field_lines:
                    prod_list.append((0, 0, {'font_size': line.font_size,
                                             'font_color': line.font_color,
                                             'sequence': line.sequence,
                                             'name': line.name}))
                res.update({'height': wiz.height,
                            'width': wiz.width,
                            'currency_id': wiz.currency_id.id,
                            'currency_position': wiz.currency_position,
                            'disp_height': wiz.disp_height,
                            'disp_width': wiz.disp_width,
                            'barcode_type': wiz.barcode_type,
                            'field_lines': prod_list
                            })
        return res

    def _get_currency(self):
        ''' when u save Product Label Template then it will get currency id'''
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    name = fields.Char(string="Design Name")
    active = fields.Boolean(string="Active", default=1)
    height = fields.Float(string="Height", required=True, default=30)
    width = fields.Float(string="Width", required=True, default=43)
    currency_id = fields.Many2one('res.currency', string="Currency", default=_get_currency)
    currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default='after')
    disp_height = fields.Float(string="Display Height (px)", required=True, default=30)
    disp_width = fields.Float(string="Display Width (px)", required=True, default=120)
    barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                     ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                     ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                     ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                     ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                     ('QR', 'QR')],
                                    string='Type', default='EAN13')
    field_lines = fields.One2many('aces.small.barcode.template.line', 'barcode_label_id', string="Fields")


class AcesSmallBarcodeTemplateLine(models.Model):
    _name = 'aces.small.barcode.template.line'

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
    barcode_label_id = fields.Many2one('aces.small.barcode.template', string="Barcode Label ID")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
