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

import logging
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class ProductSmallLabelDesign(models.Model):
    _name = 'product.small.label.design'
    _description = 'Product Small Label Design'

    def _get_currency(self):
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    @api.model
    def default_get(self, fields_list):
        res = super(ProductSmallLabelDesign, self).default_get(fields_list)
        if self._context.get('wiz_id') and self._context.get('from_wizard'):
            for wiz in self.env['wizard.product.small.label.report'].browse(self._context.get('wiz_id')):
                prod_list = []
                for field_line in wiz.product_field_lines:
                    prod_list.append((0, 0, {
                        'font_size': field_line.font_size,
                        'font_color': field_line.font_color,
                        'sequence': field_line.sequence,
                        'field_id': field_line.field_id.id,
                        'field_width': field_line.field_width,
                        'margin_value': field_line.margin_value,
                        'with_currency': field_line.with_currency
                    }))
                res.update({
                    'template_label_design': wiz.report_design,
                    'report_model': wiz.report_model,
                    'label_width': wiz.label_width,
                    'label_height': wiz.label_height,
                    'dpi': wiz.dpi,
                    'margin_top': wiz.margin_top,
                    'margin_left': wiz.margin_left,
                    'margin_bottom': wiz.margin_bottom,
                    'margin_right': wiz.margin_right,
                    'humanReadable': wiz.humanReadable,
                    'barcode_height': wiz.barcode_height,
                    'barcode_width': wiz.barcode_width,
                    'display_height': wiz.display_height,
                    'display_width': wiz.display_width,
                    'with_barcode': wiz.with_barcode,
                    'label_logo': wiz.label_logo,
                    'product_field_lines': prod_list,
                    'barcode_type': wiz.barcode_type,
                    'currency_id': wiz.currency_id and wiz.currency_id.id,
                    'currency_position': wiz.currency_position,
                    'design_using' : wiz.design_using,
                    'logo_position': wiz.logo_position,
                    'logo_height': wiz.logo_height,
                    'logo_width': wiz.logo_width,
                    'barcode_field': wiz.barcode_field
                })
        return res

    name = fields.Char(string="Design Name")
    report_model = fields.Char(string='Model')
    template_label_design = fields.Text(string="Template Design")
    # label
    label_width = fields.Integer(string='Label Width (mm)', default=43, required=True)
    label_height = fields.Integer(string='Label Height (mm)', default=30, required=True)
    dpi = fields.Integer(string='DPI', default=80, help="The number of individual dots\
                                that can be placed in a line within the span of 1 inch (2.54 cm)")
    margin_top = fields.Integer(string='Margin Top (mm)', default=4)
    margin_left = fields.Integer(string='Margin Left (mm)', default=1)
    margin_bottom = fields.Integer(string='Margin Bottom (mm)', default=1)
    margin_right = fields.Integer(string='Margin Right (mm)', default=1)
    # barcode
    humanReadable = fields.Boolean(string="HumanReadable", help="User wants to print barcode number\
                                    with barcode label.")
    barcode_height = fields.Integer(string="Height", default=300, required=True, help="This height will\
                                    required for the clearity of the barcode.")
    barcode_width = fields.Integer(string="Width", default=1500, required=True, help="This width will \
                                    required for the clearity of the barcode.")
    display_height = fields.Integer(string="Display Height (px)", required=True, default=30,
                                    help="This height will required for display barcode in label.")
    display_width = fields.Integer(string="Display Width (px)", required=True, default=120,
                                   help="This width will required for display barcode in label.")
    with_barcode = fields.Boolean(string='Barcode', help="Click this check box if user want to print\
                                    barcode for Product Label.", default=True)
    active = fields.Boolean(string="Active", default=True)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    label_logo = fields.Binary(string="Label Logo")
    design_using = fields.Selection([('fields_selection', 'Fields Selection'),
                                     ('xml_design', 'XML Design')],
                                    default='xml_design')
    product_field_lines = fields.One2many('aces.design.field.line', 'design_id', string="Product Fields")
    barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                     ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                     ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                     ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                     ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                     ('QR', 'QR')], string="Barcode Type")
    currency_id = fields.Many2one('res.currency', string="Currency", default=_get_currency)
    currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default="before")
    logo_position = fields.Selection([('top', 'Top'), ('bottom', 'Bottom')], string="Logo Position")
    logo_height = fields.Integer(string="Logo Height(px)")
    logo_width = fields.Integer(string="Logo width(px)")
    barcode_field = fields.Selection([('barcode', 'Barcode'), ('default_code', 'Internal Reference')],
                                     string="Barcode Field", default="barcode")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_wizard') and self._context.get('report_model'):
            args.append(('report_model', '=', self._context.get('report_model')))
        elif self._context.get('from_wizard') and not self._context.get('report_model'):
            args.append(('report_model', '=', False))
        return super(ProductSmallLabelDesign, self).name_search(name, args=args, operator=operator, limit=limit)

    def close_wizard(self):
        self.write({'active': False})
        return {
            'name': _('Print Product Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.product.small.label.report',
            'target': 'new',
            'res_id': self._context.get('wiz_id') ,
            'context': self.env.context
        }

    def go_to_label_wizard(self):
        if not self.name:
            raise UserError(_('Label Design Name is required.'))
        return {
            'name': _('Product Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.product.small.label.report',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_wizard') and self._context.get('product_id'):
            product_record = self.env['product.product'].browse([self._context.get('product_id')])
            args.append(('id', 'in', [attribute.id for attribute in product_record.attribute_line_ids]))
        return super(ProductAttributeValue, self).name_search(name, args, operator='ilike', limit=limit)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals):
        record = super(SaleOrder, self).create(vals)
        record.action_confirm()
        data = json.loads(record.tax_totals_json)
        vals = {'advance_payment_method': 'delivered',
                'deduct_down_payments': True,
                'product_id': False,
                'currency_id': record.currency_id.id,
                'fixed_amount': data['amount_total'],
                'amount': data['amount_total'],
                'deposit_account_id': False,
                'deposit_taxes_id': [[6, False, []]]}
        record_id = self.env['sale.advance.payment.inv'].sudo().with_context(active_ids=[record.id]).create(vals)
        record_id.create_invoices()
        return record


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model_create_multi
    def create(self, vals):
        record = super(SaleAdvancePaymentInv, self).create(vals)
        return record

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
