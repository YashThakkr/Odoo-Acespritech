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
from odoo.exceptions import UserError


class product_page_label_design(models.Model):
    _name = 'product.page.label.design'
    _description = 'Product Page Lable Design'

    @api.model
    def default_get(self, fields_list):
        res = super(product_page_label_design, self).default_get(fields_list)
        if self._context.get('wiz_id') and self._context.get('from_wizard'):
            for wiz in self.env['wizard.product.page.report'].browse(self._context.get('wiz_id')):
                res.update({
                    'page_template_design': wiz.column_report_design,
                    'report_model': wiz.report_model,
                    'page_width': wiz.page_width, 'page_height': wiz.page_height,
                    'dpi': wiz.dpi, 'humanReadable': wiz.humanReadable,
                    'margin_top': wiz.margin_top, 'margin_bottom': wiz.margin_bottom,
                    'margin_left': wiz.margin_left, 'margin_right': wiz.margin_right,
                    'orientation': wiz.orientation, 'with_barcode': wiz.with_barcode,
                    'barcode_height': wiz.barcode_height, 'barcode_width': wiz.barcode_width,
                    'display_height': wiz.display_height, 'display_width': wiz.display_width,
                    'format': wiz.format, 'col_no': wiz.col_no,
                    'col_width': wiz.col_width, 'col_height': wiz.col_height,
                    'label_logo': wiz.label_logo
                })
        return res

    name = fields.Char(string="Design Name")
    report_model = fields.Char(string='Model')
    page_template_design = fields.Text(string="Report Design")
    # page
    page_width = fields.Integer(string='Page Width (mm)', default=210)
    page_height = fields.Integer(string='Page Height (mm)', default=297)
    dpi = fields.Integer(string='DPI', default=80, help="The number of individual dots\
                                that can be placed in a line within the span of 1 inch (2.54 cm)")
    margin_top = fields.Integer(string='Margin Top (mm)', default=1)
    margin_left = fields.Integer(string='Margin Left (mm)', default=1)
    margin_bottom = fields.Integer(string='Margin Bottom (mm)', default=1)
    margin_right = fields.Integer(string='Margin Right (mm)', default=1)
    orientation = fields.Selection([('Landscape', 'Landscape'),
                                    ('Portrait', 'Portrait')],
                                   string='Orientation', default='Portrait', required=True)
    # barcode
    humanReadable = fields.Boolean(string="HumanReadable", help="User wants to print barcode number\
                                    with barcode page label.")
    barcode_height = fields.Integer(string="Height", default=300, required=True, help="This height will\
                                    required for the clearity of the barcode.")
    barcode_width = fields.Integer(string="Width", default=1500, required=True, help="This width will \
                                    required for the clearity of the barcode.")
    display_height = fields.Integer(string="Display Height (px)", required=True, default=40,
                                    help="This height will required for display barcode in page label.")
    display_width = fields.Integer(string="Display Width (px)", required=True, default=200,
                                    help="This width will required for display barcode in page label.")
    with_barcode = fields.Boolean(string='Barcode', help="Click this check box if user want to print\
                                    barcode for Product Page Label.", default=True)
    # new columns and rows fields
    format = fields.Selection([('A0', 'A0  5   841 x 1189 mm'),
                               ('A1', 'A1  6   594 x 841 mm'),
                               ('A2', 'A2  7   420 x 594 mm'),
                               ('A3', 'A3  8   297 x 420 mm'),
                               ('A4', 'A4  0   210 x 297 mm, 8.26 x 11.69 inches'),
                               ('A5', 'A5  9   148 x 210 mm'),
                               ('A6', 'A6  10  105 x 148 mm'),
                               ('A7', 'A7  11  74 x 105 mm'),
                               ('A8', 'A8  12  52 x 74 mm'),
                               ('A9', 'A9  13  37 x 52 mm'),

                               ('B0', 'B0  14  1000 x 1414 mm'),
                               ('B1', 'B1  15  707 x 1000 mm'),
                               ('B2', 'B2  17  500 x 707 mm'),
                               ('B3', 'B3  18  353 x 500 mm'),
                               ('B4', 'B4  19  250 x 353 mm'),
                               ('B5', 'B5  1   176 x 250 mm, 6.93 x 9.84 inches'),
                               ('B6', 'B6  20  125 x 176 mm'),
                               ('B7', 'B7  21  88 x 125 mm'),
                               ('B8', 'B8  22  62 x 88 mm'),
                               ('B9', 'B9  23  33 x 62 mm'),
                               ('B10', ':B10    16  31 x 44 mm'),

                               ('C5E', 'C5E 24  163 x 229 mm'),
                               ('Comm10E', 'Comm10E 25  105 x 241 mm, U.S. '
                                'Common 10 Envelope'),

                               ('DLE', 'DLE 26 110 x 220 mm'),

                               ('Executive', 'Executive 4   7.5 x 10 inches, '
                                '190.5 x 254 mm'),

                               ('Folio', 'Folio 27  210 x 330 mm'),

                               ('Ledger', 'Ledger  28  431.8 x 279.4 mm'),
                               ('Legal', 'Legal    3   8.5 x 14 inches, '
                                '215.9 x 355.6 mm'),
                               ('Letter', 'Letter 2 8.5 x 11 inches, '
                                '215.9 x 279.4 mm'),
                               ('Tabloid', 'Tabloid 29 279.4 x 431.8 mm'),

                               ('custom', 'Custom')],
                               string='Paper Type', default="custom",
                               help="Select Proper Paper size")
    col_no = fields.Integer('No. of Column', default=1)
    col_width = fields.Float('Column Width (mm)', default=52.5)
    col_height = fields.Float('Column Height (mm)', default=29.7)
    from_col = fields.Integer(string="Start Column", default=1)
    from_row = fields.Integer(string="Start Row", default=1)
    active = fields.Boolean(string="Active", default=True)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    label_logo = fields.Binary(string="Label Logo")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_wizard') and self._context.get('report_model'):
            args.append(('report_model', '=', self._context.get('report_model')))
        elif self._context.get('from_wizard') and not self._context.get('report_model'):
            args.append(('report_model', '=', False))
        return super(product_page_label_design, self).name_search(name, args=args, operator=operator, limit=limit)

    def close_wizard(self):
        self.write({'active': False})
        return {
            'name': _('Print Product Page Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.product.page.report',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }

    def go_to_label_wizard(self):
        if not self.name:
            raise UserError(_('Page Label Design Name is required.'))
        return {
            'name': _('Product Page Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.product.page.report',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
