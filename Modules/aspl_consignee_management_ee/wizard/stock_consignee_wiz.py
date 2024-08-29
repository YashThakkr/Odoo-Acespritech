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

import base64

import xlsxwriter
from odoo import models, fields


class WizardConsigneeReport(models.TransientModel):
    _name = "wizard.consignee.report"
    _description = 'Wizard Consignee Report'

    from_date = fields.Date(string="Start Date")
    to_date = fields.Date(string="End Date")
    view_report = fields.Selection(
        [('product_wise', 'Product Wise'), ('consignee_wise', 'Consignee Wise')],
        string="View Report")
    product_ids = fields.Many2many('product.product', string="Product")
    consignee_ids = fields.Many2many('res.partner', string="Consignee",
                                     domain=[('is_consignee', '=', True)])

    def compute_quantities_dict(self):
        final_dict = {}
        if self.view_report == 'product_wise':
            product_ids = self.product_ids
            if not product_ids:
                product_ids = self.env['product.product'].search([('type', '=', 'product')])

            consignee_dict = dict((partner['location_id'][0], partner['id'])
                                  for partner in
                                  self.env['res.partner'].search_read([('is_consignee', '=', True),
                                                                       ('location_id', '!=', False)], ['location_id']))
            if consignee_dict and product_ids:
                for product in product_ids:
                    final_dict.update({product.name: []})
                    domain_quant = [('create_date', '>=', self.from_date),
                                    ('create_date', '<=', self.to_date),
                                    ('product_id', '=', product.id),
                                    ('location_id', 'in', list(consignee_dict.keys()))]
                    quants_res = [{'location_id': self.env['stock.location'].browse(
                        item['location_id'][0]).display_name,
                                   'consignee_id': self.env['res.partner'].browse(
                                       consignee_dict.get(item['location_id'][0])).name,
                                   'quantity': item['quantity']}
                                  for item in self.env['stock.quant'].read_group(domain_quant,
                                                                                 ['product_id',
                                                                                  'quantity',
                                                                                  'location_id'],
                                                                                 ['location_id'])]
                    if quants_res:
                        final_dict[product.name].append(quants_res[0])
                    else:
                        final_dict.pop(product.name)

        if self.view_report == 'consignee_wise':
            consignee_ids = self.consignee_ids
            if not consignee_ids:
                consignee_ids = self.env['res.partner'].search([('is_consignee', '=', True),
                                                                ('location_id', '!=', False)])
            for consignee in consignee_ids:
                final_dict.update({consignee.name: []})
                domain_quant = [('create_date', '>=', self.from_date),
                                ('create_date', '<=', self.to_date),
                                ('location_id', '=', consignee.location_id.id)]
                quants_res = [
                    {'product_id': self.env['product.product'].browse(item['product_id'][0]).name,
                     'quantity': item['quantity']}
                    for item in self.env['stock.quant'].read_group(domain_quant,
                                                                   ['product_id', 'quantity',
                                                                    'location_id'],
                                                                   ['product_id'])]
                if quants_res:
                    final_dict[consignee.name].append(quants_res[0])
                else:
                    final_dict.pop(consignee.name)

        final_keys = final_dict.keys()
        return [final_keys, final_dict]

    def generate_consignee_report(self):
        workbook = xlsxwriter.Workbook('temp_file' + '.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format = workbook.add_format({'bold': True, 'align': 'center'})
        merge_format.set_underline()
        merge_format_bold = workbook.add_format({'bold': True, })
        worksheet.merge_range('D1:F2', "Consignee Report", merge_format)
        dates = str(self.from_date) + " - " + str(self.to_date)
        worksheet.merge_range('D3:F3', dates, )
        worksheet.set_column('A:A', 25)
        worksheet.set_column('C:C', 15)

        if self.view_report == 'product_wise':
            product_qty_dict = self.compute_quantities_dict()
            if product_qty_dict and product_qty_dict[0] and product_qty_dict[1]:
                row = 4
                col = 0
                for product in product_qty_dict[0]:
                    worksheet.write(row, col, product, merge_format, )
                    row = row + 1
                    col = 0
                    worksheet.write(row, col, 'Consignee', merge_format_bold)
                    worksheet.write(row, col + 2, 'Location', merge_format_bold)
                    worksheet.write(row, col + 4, 'Quantity', merge_format_bold)
                    row = row + 1
                    col = 0
                    for consignee_detail in product_qty_dict[1].get(product):
                        worksheet.write(row, col, consignee_detail['consignee_id'])
                        worksheet.write(row, col + 2, consignee_detail['location_id'])
                        worksheet.write(row, col + 4, consignee_detail['quantity'])
                        row = row + 1
                    row = row + 1

        if self.view_report == 'consignee_wise':
            consignee_qty_dict = self.compute_quantities_dict()
            if consignee_qty_dict:
                row = 4
                col = 0
                for consignee in consignee_qty_dict[0]:
                    worksheet.write(row, col, consignee, merge_format)
                    row = row + 1
                    col = 0
                    worksheet.write(row, col, 'Product', merge_format_bold)
                    worksheet.write(row, col + 2, 'Quantity', merge_format_bold)
                    row = row + 1
                    col = 0
                    for product_detail in consignee_qty_dict[1].get(consignee):
                        worksheet.write(row, col, product_detail['product_id'])
                        worksheet.write(row, col + 2, product_detail['quantity'])
                        row = row + 1
                    row = row + 1

        workbook.close()
        buf = base64.encodebytes(open('temp_file' + '.xlsx', 'rb').read())
        form_id = self.env.ref('aspl_consignee_management_ee.stock_consignee_view_down_report')
        report_rec = self.env['wiz.consignee.dwn.report'].create(
            {'file': buf, 'name': 'Stock Consignee Report.xlsx'})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': report_rec.id,
            'res_model': 'wiz.consignee.dwn.report',
            'views': [(form_id.id, 'form')],
            'view_id': form_id.id,
            'target': 'new',
        }


class WizConsigneeDwnReport(models.TransientModel):
    _name = "wiz.consignee.dwn.report"
    _description = 'Consignee Download Report'

    name = fields.Char(string="Name")
    file = fields.Binary(string="File To download")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
