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

import binascii
import tempfile

import xlrd
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ConsigneeImportTransfer(models.TransientModel):
    _name = 'consignee.import.transfer'
    _description = 'Consignee Import Transfer'

    import_type = fields.Selection([
        ('consignee_transfer', 'Consignee Transfer'),
        ('consignee_return_transfer', 'Consignee Return Transfer'),
        ('consignee_to_consignee_transfer', 'Consignee To Consignee Transfer'),
        ('consume_item', 'Consume Item Transfer')
    ])
    data_file = fields.Binary(string="Choose File")
    partner_id = fields.Many2one('res.partner', string="Consignee",
                                 domain=[('is_consignee', '=', True), ('location_id', '!=', False)])
    source_location_id = fields.Many2one('stock.location', string='Source Location')
    destination_location_id = fields.Many2one('stock.location', string='Destination Location')
    to_partner_id = fields.Many2one('res.partner', string='To Consignee',
                                    domain=[('is_consignee', '=', True)])
    import_by = fields.Selection([('barcode', 'Barcode'),
                                  ('internal_ref', 'Internal Reference')], string="Import using")

    def import_consignee(self):
        product_obj = self.env['product.product']
        if not self.data_file:
            raise ValidationError(_('Please select file to import...!'))

        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.data_file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        line_lst = []
        vals = {}

        if self.import_type == 'consume_item':
            if self.partner_id:
                for row_no in range(sheet.nrows):
                    if row_no <= 0:
                        map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = sheet.row_values(row_no)
                        if self.import_by == 'barcode':
                            product_id = product_obj.search([('barcode', '=', line[0].strip())],
                                                            limit=1)
                        else:
                            product_id = product_obj.search(
                                [('default_code', '=', line[0].strip())], limit=1)
                        if product_id:
                            line_lst.append((0, 0, {
                                'product_id': product_id.id,
                                'consumed_qty': line[1],
                                'uom_id': product_id.uom_id.id
                            }))
                if line_lst:
                    consume_items_id = self.env['consignee.consume.items'].create(
                        {'partner_id': self.partner_id.id, 'customers_consignee_line': line_lst})
                    create_sale_order = self.env['ir.config_parameter'].sudo().get_param(
                        'aspl_consignee_management_ee.on_consume_item_import')
                    if create_sale_order:
                        consume_items_id.action_done()
        else:
            if self.import_type == 'consignee_transfer':
                if self.partner_id and self.source_location_id:
                    vals = {'partner_id': self.partner_id.id,
                            'destination_location_id': self.partner_id.location_id.id,
                            'source_location_id': self.source_location_id.id}

            if self.import_type == 'consignee_return_transfer':
                if self.partner_id and self.destination_location_id:
                    vals = {'partner_id': self.partner_id.id,
                            'is_return': True,
                            'source_location_id': self.partner_id.location_id.id,
                            'destination_location_id': self.destination_location_id.id}

            if self.import_type == 'consignee_to_consignee_transfer':
                if self.partner_id and self.to_partner_id:
                    vals = {'partner_id': self.partner_id.id,
                            'is_internal_transfer': True,
                            'to_partner_id': self.to_partner_id.id,
                            'source_location_id': self.partner_id.location_id.id,
                            'destination_location_id': self.to_partner_id.location_id.id}

            for row_no in range(sheet.nrows):
                if row_no <= 0:
                    map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = sheet.row_values(row_no)

                    if self.import_by == 'barcode':
                        product_id = product_obj.search([('barcode', '=', line[0].strip())],
                                                        limit=1)
                    else:
                        product_id = product_obj.search([('default_code', '=', line[0].strip())],
                                                        limit=1)
                    if product_id:
                        line_lst.append((0, 0, {
                            'product_id': product_id.id,
                            'requested_qty': line[1],
                            'transfer_qty': line[2],
                            'uom_id': product_id.uom_id.id,
                        }))
            if line_lst:
                vals.update({'lines': line_lst})
                self.env['stock.consignee.transfer'].create(vals)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
