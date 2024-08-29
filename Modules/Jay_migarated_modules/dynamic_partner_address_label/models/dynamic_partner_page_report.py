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

from odoo import models, api, _
from base64 import b64encode
import math
from reportlab.graphics import barcode


class DynamicPartnerAddressReportTemp(models.AbstractModel):
    _name = 'report.dynamic_partner_address_label.dynamic_partner_page_rpt'
    _description = 'Dynamic Partner Page Report'

    def _get_style(self, data):
        return 'height:' + str(data['form']['display_height']) + 'px;width:' + str(data['form']['display_width']) + 'px;'

    def _draw_style(self, data):
        return 'width:' + str(data['form']['col_width']) + 'mm !important;height:' + str(data['form']['col_height']) + 'mm !important; margin: 0px 0px 0px 0px; padding: 0px; overflow: hidden !important; text-overflow: ellipsis !important;'

    def get_cell_number(self, from_row, from_col, col_no):
        return ((from_row - 1) * col_no + from_col - 1)

    def _draw_table(self, data):
        partner_list = []
        if data['form']['partner_ids']:
            cell_no = self.get_cell_number(data['form']['from_row'], data['form']['from_col'], int(data['form']['col_no']))
            box_needed = int(cell_no) or 0
            for partner_data in self.env['partner.page.label.qty'].browse(data['form']['partner_ids']):
                if partner_data.partner_id:
                    box_needed += int(partner_data.qty)
                    partner_list.append(partner_data)
            cell_record = self.create_list(partner_list, int(cell_no))
            _table = self.create_table(box_needed, cell_record, data)
            return _table

    def _get_barcode(self, value, type, data):
        barcode_str = ''
        if data['form']['with_barcode'] and value and type:
            try:
                barcode_str = barcode.createBarcodeDrawing(
                                    type, value=value, format='png', width=int(data['form']['barcode_height']),
                                    height=int(data['form']['barcode_width']), humanReadable=data['form']['humanReadable'])
            except Exception:
                return ''
            barcode_str = b64encode(barcode_str.asString('png'))
        return barcode_str

    def create_list(self, partners, cell_no):
        model = ''
        if self._context.get('active_model') in ('sale.order', 'purchase.order', 'stock.picking', 'account.move'):
            model = self._context.get('active_model')

        partner_data = {}
        for partner in partners:
            if partner.line_id and model and partner.line_id:
                record_brw = self.env[model].browse(partner.line_id)
                for qty in range(0, int(partner.qty)):
                    partner_data.update({cell_no: {'partner_id': record_brw}})
                    cell_no += 1

            elif partner.partner_id and not partner.line_id:
                for qty in range(0, int(partner.qty)):
                    partner_data.update({cell_no: {'partner_id': partner.partner_id}})
                    cell_no += 1
        return partner_data

    def create_table(self, box_needed, cell_record, data):
        no_of_col = int(data['form']['col_no'])
        partner_table = []
        for tr_no in range(1, int(math.ceil(float(box_needed) / no_of_col + 1))):
            partner_dict = {}
            for td_no in range(1, no_of_col + 1):
                cellno = self.get_cell_number(tr_no, td_no, no_of_col)
                if cellno in cell_record:
                    partner_id = cell_record.get(cellno).get('partner_id')
                    if tr_no in partner_dict:
                        partner_dict[tr_no].append(partner_id)
                    else:
                        partner_dict[tr_no] = [partner_id]
                else:
                    if tr_no in partner_dict:
                        partner_dict[tr_no].append(False)
                    else:
                        partner_dict[tr_no] = [False]
            partner_table.append(partner_dict)
        return partner_table

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('dynamic_partner_address_label.dynamic_partner_page_rpt')
        return {
            'doc_ids': self.env["wizard.partner.page.report"].browse(data["ids"]),
            'doc_model': report.model,
            'docs': self,
            'draw_table': self._draw_table,
            'get_barcode': self._get_barcode,
            'draw_style': self._draw_style,
            'get_style': self._get_style,
            'data': data
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
