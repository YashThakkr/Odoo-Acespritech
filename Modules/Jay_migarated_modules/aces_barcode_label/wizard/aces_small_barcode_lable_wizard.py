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


class AcesSmallBarcodeLabel(models.TransientModel):
    _name = 'aces.small.barcode.label'

    @api.onchange('design_id')
    def on_change_design_id(self):
        if self.design_id:
            prod_list = []
            for line in self.design_id.field_lines:
                print("\n\n\n line")
                prod_list.append((0, 0, {'font_size': line.font_size,
                                         'font_color': line.font_color,
                                         'sequence': line.sequence,
                                         'name': line.name}))
            self.height = self.design_id.height
            self.width = self.design_id.width
            self.currency_id = self.design_id.currency_id and self.design_id.currency_id.id or False
            self.currency_position = self.design_id.currency_position
            self.disp_height = self.design_id.disp_height
            self.disp_width = self.design_id.disp_width
            self.barcode_type = self.design_id.barcode_type
            self.field_lines = prod_list
            print("\n\n\ prod_list = []", prod_list)

    @api.model
    def default_get(self, fields_list):
        ''' get active_id for product'''
        prod_list = []
        res = super(AcesSmallBarcodeLabel, self).default_get(fields_list)
        if self._context.get('active_ids'):
            for product in self._context.get('active_ids'):
                prod_list.append((0, 0, {'product_id': product, 'qty': 1}))
        res['product_lines'] = prod_list
        return res

    def _get_currency(self):
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    @api.model
    def _get_report_paperformat_id(self):
        ''' get report id'''
        xml_id = self.env['ir.actions.report'].search([('report_name', '=',
                                                        'aces_barcode_label.product_barcode_report_template')])
        if not xml_id or not xml_id.paperformat_id:
            raise UserError('Someone has deleted the reference paperformat of report.Please Update the module!')
        return xml_id.paperformat_id.id

    design_id = fields.Many2one('aces.small.barcode.template', string="Design")
    paper_format_id = fields.Many2one('report.paperformat', string="Paper Format", default=_get_report_paperformat_id)
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
    field_lines = fields.One2many('aces.small.barcode.label.line', 'barcode_label_id', string="Fields")
    product_lines = fields.One2many('aces.small.product.label.qty', 'barcode_label_id', string="Product List")
    make_update_existing = fields.Boolean(string="Update Existing Design")
    image_height = fields.Integer(string="Height(px)")
    image_width = fields.Integer(string="Width(px)")

    def action_call_report(self):
        '''Prints label report for user'''
        line_seq = []
        line_name = []
        if self.height <= 0.0 or self.width <= 0.0:
            raise UserError(_("Label height and width should be greater than zero(0)."))
        if not self.field_lines:
            raise UserError(_("Please select any one field to print in label."))
        for line in self.field_lines:
            if line.name == 'barcode' and (not self.barcode_type or self.disp_height <= 0.0 or self.disp_width <= 0.0):
                raise UserError(
                    _("To print barcode enter appropriate data in barcode type, display height and width fields."))
            if not line.sequence or not line.name:
                raise UserError(_("Sequence and fields name can not be empty."))
            if line.sequence in line_seq or line.name in line_name:
                raise UserError(_("Sequence and field name cannot repeated."))
            line_seq.append(line.sequence)
            line_name.append(line.name)
        if 'lst_price' in line_name and self.currency_id and not self.currency_position:
            raise UserError(_("Please, select currency position to display currency symbol."))
        if 'barcode' in line_name:
            if not [product.product_id.barcode for product in self.product_lines if product.product_id.barcode]:
                raise UserError(_("You have selected barcode to print, but none of product(s) contain(s) barcode."))
        if sum([p.qty for p in self.product_lines]) <= 0:
            raise UserError(_("Please, enter product quantity to print no. of labels."))
        self.paper_format_id.sudo().write({
            'page_width': self.width,
            'page_height': self.height
        })
        data = self.read()[0]
        datas = {
            'ids': self._ids,
            'model': 'aces.small.barcode.label',
            'form': data
        }
        return self.env.ref('aces_barcode_label.aces_small_barcode_label_report').report_action(self, data=datas)

    def save_design_template(self):
        '''For saving design template'''

        if not self.make_update_existing:
            view_id = self.env.ref('aces_barcode_label.wizard_aces_small_barcode_template_form_view').id
            ctx = dict(self.env.context)
            ctx.update({'wiz_id': self.id})
            return {
                'name': _('Product Label Template'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'aces.small.barcode.template',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'view_id': view_id,
                'context': ctx,
                'nodestroy': True
            }
        else:
            prod_list = []
            if self.design_id:
                for line in self.field_lines:
                    prod_list.append((0, 0, {'font_size': line.font_size,
                                             'font_color': line.font_color,
                                             'sequence': line.sequence,
                                             'name': line.name}))
                self.design_id.field_lines = False
                self.design_id.write({
                    'height': self.height,
                    'width': self.width,
                    'currency_id': self.currency_id.id,
                    'currency_position': self.currency_position,
                    'disp_height': self.disp_height,
                    'disp_width': self.disp_width,
                    'barcode_type': self.barcode_type,
                    'field_lines': prod_list
                })
                return {
                    'name': _('Product Page Label'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'aces.small.barcode.label',
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context
                }
            else:
                raise UserError(_("Please, select design template first !"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
