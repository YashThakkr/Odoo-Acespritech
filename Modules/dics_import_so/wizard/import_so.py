# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError
import base64
import xlrd
import logging
import io
import openpyxl
from datetime import datetime, timedelta
from datetime import date

#******* requirement openpyxl *********
#     pip install openpyxl


class ImportEventWiz(models.TransientModel):
    _name = 'import.so.wiz'
    _description = 'Import Event Wiz'

    file = fields.Binary(string="File", required=True)
    file_name = fields.Char()

    def import_so(self):
        print ('>>>>>>>>>>>>>>>>>>>>>>>.')
        # Get the binary data from the wizard's binary field.
        xls_data = io.BytesIO(base64.b64decode(self.file))

        # Load the XLS file using openpyxl.
        try:
            workbook = openpyxl.load_workbook(xls_data, data_only=True)
            sheet = workbook.active
        except Exception as e:
            return {
                'warning': {
                    'title': 'Error',
                    'message': f'Error loading XLS file: {str(e)}',
                }
            }

        sale_order_obj = self.env['sale.order']
        for row in sheet.iter_rows(min_row=2, values_only=True):
            sale_order_number = row[0]  # Assuming the sale order number is in the first column.

            # Check if the sale order exists.
            sale_order = sale_order_obj.search([('name', '=', sale_order_number)])
            if sale_order:
                print ('sale order  ',sale_order)
                # Confirm the sale order.
                sale_order.action_confirm()

                if sale_order.picking_ids:
                    for picking in sale_order.picking_ids:
                        picking.immediate_transfer = True
                        for move in picking.move_ids:
                            move.quantity_done = move.product_uom_qty
                        picking._autoconfirm_picking()
                        picking.action_set_quantities_to_reservation()
                        picking.action_confirm()
                        for move_line in picking.move_ids_without_package:
                            move_line.quantity_done = move_line.product_uom_qty
                        picking._action_done()
                        for mv_line in picking.move_ids.mapped('move_line_ids'):
                            if not mv_line.qty_done and mv_line.reserved_qty or mv_line.reserved_uom_qty:
                                mv_line.qty_done = mv_line.reserved_qty or mv_line.reserved_uom_qty
                sale_order._create_invoices()


