# -*- coding: utf-8 -*-
from odoo import fields, models, _
import base64
import io
import openpyxl
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, MissingError, ValidationError


# ******* requirement openpyxl *********
#     pip install openpyxl


class ImportInvWiz(models.TransientModel):
    _name = 'import.inv.wiz'
    _description = 'Import Invoice Wiz'

    file = fields.Binary(string="File", required=True)
    file_name = fields.Char()

    def import_inv(self):
        # Get the binary data from the wizard's binary field.
        xls_data = io.BytesIO(base64.b64decode(self.file))
        workbook = openpyxl.load_workbook(xls_data, data_only=True)
        # Load the XLS file using openpyxl.
        try:
            list_not_import = []
            for sheet in workbook.worksheets:
                # sheet = workbook.active
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    partner = self.env['res.partner'].search([('name', '=', row[1])], limit=1)
                    if not partner:
                        partner = self.env['res.partner'].create({
                            'name': row[1],
                            'customer_code': row[0]
                        })
                        self.env.cr.commit()
                    account_move_id = self.env['account.move'].search(
                        [('name', '=', row[3]), ('is_xlsx_data', '=', True)], limit=1)
                    move_type = {
                        'IN': 'out_invoice',
                        'PU': 'in_invoice',
                        'JE': 'in_refund',
                        'CN': 'out_refund',
                    }
                    posting_date = datetime.strptime(str(row[4]), '%Y-%m-%d %H:%M:%S').date()
                    invoice_date_due = datetime.strptime(str(row[5]), '%Y-%m-%d %H:%M:%S').date()
                    document_date = datetime.strptime(str(row[6]), '%Y-%m-%d %H:%M:%S').date()

                    # account_id = self.env['account.account'].search([('code', '=', row[10])], limit=1)
                    account_sale = self.env['account.account'].search([('code', '=', "4100100001")], limit=1)
                    account_purchase = self.env['account.account'].search([('code', '=', "5100100000")], limit=1)
                    account_id = ""
                    if move_type.get(row[2]) in ['out_invoice', 'out_refund']:
                        account_id = account_sale
                    if move_type.get(row[2]) in ['in_invoice', 'in_refund']:
                        account_id = account_purchase

                    if not account_move_id:
                        vals = {
                            'partner_id': partner.id,
                            'name': row[3],
                            'is_xlsx_data': True,
                            'move_type': move_type.get(row[2]),
                            'invoice_date_due': invoice_date_due,
                            'invoice_payment_term_id': False,
                            'invoice_date': posting_date,
                            'document_date': document_date,
                            'invoice_line_ids': [(0, 0, {
                                'name': row[7],
                                'account_id': account_id.id,
                                'quantity': 1,
                                'price_unit': abs(row[8]) if isinstance(row[8], int) else 1,
                                'log': "In Xlsx Original Amount Is not Integer Value then Amount is 1" if not isinstance(
                                    row[8], int) else False,
                            })],
                        }
                        account_move_id = self.env['account.move'].create(vals)
                        self.env.cr.commit()

                    if not account_move_id:
                        list_not_import.append(row[3])

            if list_not_import:
                inv_no = ""
                for list in list_not_import:
                    inv_no += str(str("Not Imported Record Id Is : " + str(list)) + "\n")
                wizard = self.env['not.imp.inv.wiz'].create({
                    'not_import_inv': inv_no,
                })
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Not Imported Accounting',
                    'view_mode': 'form',
                    'res_model': 'not.imp.inv.wiz',
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
