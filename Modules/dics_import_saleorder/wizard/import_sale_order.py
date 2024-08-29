# -*- coding: utf-8 -*-
from odoo import fields, models, _
import base64
import io
import openpyxl
from datetime import datetime, date
from odoo.exceptions import AccessError, MissingError, ValidationError


class ImportSaleorderWiz(models.TransientModel):
    _name = 'import.saleorder.wiz'
    _description = 'Import Sale Order Wiz'

    file = fields.Binary(string="File", required=True)
    file_name = fields.Char()

    def import_sale_order(self):
        # Get the binary data from the wizard's binary field.
        xls_data = io.BytesIO(base64.b64decode(self.file))
        workbook = openpyxl.load_workbook(xls_data, data_only=True)
        # Load the XLS file using openpyxl.
        try:
            list_not_import = []
            list_line_not_import = []
            list_sales = []
            for sheet in workbook.worksheets:
                # sheet = workbook.active
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    partner_id = self.env['res.partner'].search([('customer_code', '=', row[0])], limit=1)
                    if not partner_id:
                        list_not_import.append(str("[%s] Customer not found : %s" % (row[0], row[0])))
                        list_line_not_import.append(row[2])

                    if partner_id:
                        child_partner_id = self.env['res.partner'].search(
                            [('name', '=', row[1]), ('parent_id', '=', partner_id.id)], limit=1)

                        if not child_partner_id:
                            list_not_import.append(str("Customer [%s] Shipping not found : %s" % (row[0], row[1])))
                            list_line_not_import.append(row[2])

                        if child_partner_id:
                            if row[2]:
                                product_variant_id = self.env['product.product'].search(
                                    [('default_code', '=', row[3])], limit=1)
                                if not product_variant_id:
                                    list_not_import.append(
                                        str("Customer [%s] Product not found : %s" % (row[0], row[3])))
                                    list_line_not_import.append(row[2])

                                currency_id = self.env['res.currency'].search([('name', '=', row[6])], limit=1)
                                if not currency_id:
                                    list_not_import.append(
                                        str("Customer [%s] Currency not found : %s" % (row[0], row[6])))
                                    list_line_not_import.append(row[2])

                                if product_variant_id:
                                    demand_date = datetime.strptime(str(row[7]), '%Y.%m.%d')
                                    vals = {
                                        'partner_id': partner_id.id,
                                        'partner_shipping_id': child_partner_id.id,
                                        'currency_id': currency_id.id if currency_id else product_variant_id.currency_id.id,
                                        'commitment_date': demand_date,
                                        'product_id': product_variant_id.id,
                                        'product_template_id': product_variant_id.product_tmpl_id.id,
                                        'name': product_variant_id.display_name,
                                        'product_uom_qty': row[4],
                                        'price_unit': row[5],
                                        'product_uom': product_variant_id.uom_id.id,
                                        'cus_po': row[2],
                                    }
                                    list_sales.append(vals)
            if list_sales:
                for sale in list_sales:
                    if sale.get('cus_po') not in list_line_not_import:
                        sale_id = self.env['sale.order'].search([('customer_po', '=', sale.get('cus_po'))], limit=1)
                        if not sale_id:
                            sale_id = self.env['sale.order'].sudo().create({
                                'partner_id': sale.get('partner_id'),
                                'partner_invoice_id': sale.get('partner_id'),
                                'partner_shipping_id': sale.get('partner_shipping_id'),
                                'currency_id': sale.get('currency_id'),
                                'commitment_date': sale.get('commitment_date'),
                                'date_order': datetime.now(),
                                'customer_po': sale.get('cus_po'),
                            })
                        sale_order_id = self.env['sale.order.line'].sudo().create({
                            'product_id': sale.get('product_id'),
                            'product_template_id': sale.get('product_template_id'),
                            'name': sale.get('name'),
                            'product_uom_qty': sale.get('product_uom_qty'),
                            'price_unit': sale.get('price_unit'),
                            'product_uom': sale.get('product_uom'),
                            'cus_po': sale.get('cus_po'),
                            'order_id': sale_id.id,
                        })
                        self.env.cr.commit()

            new_list_not_import = []
            if list_not_import:
                for dictionary in list_not_import:
                    if dictionary not in new_list_not_import:
                        new_list_not_import.append(dictionary)

                error_lst = ""
                for list in new_list_not_import:
                    error_lst += str(list + "\n")
                wizard = self.env['not.imp.so.wiz'].create({
                    'not_import_so': error_lst,
                })
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Not Imported Accounting',
                    'view_mode': 'form',
                    'res_model': 'not.imp.so.wiz',
                    'res_id': wizard.id,
                    'target': 'new',
                }


        except Exception as e:
            return {
                'warning': {
                    'title': 'Error',
                    'message': f'Error loading XLS file: {str(e)}',
                }
            }
