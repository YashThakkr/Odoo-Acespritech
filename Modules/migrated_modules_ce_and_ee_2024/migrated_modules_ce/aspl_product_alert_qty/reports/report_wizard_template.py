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

from odoo import models, api, fields


class ReportProductQtyWizardPdf(models.AbstractModel):
    _name = 'report.aspl_product_alert_qty.report_wizard_template'
    _description = "Report Product Quantity"

    @api.model
    def _get_report_values(self, docids, data=None):
        if data.get('ids'):
            record = self.env['alert.report.wizard'].browse(data['ids'])
        else:
            record = self.env['alert.report.wizard'].browse(self._context.get('wizard_id'))
        result = {'doc_ids': record,
                  'doc_model': 'alert.report.wizard',
                  'data': data,
                  'docs': record,
                  '_group_products': self.group_products}
        return result

    def group_products(self, data):
        if data.get('ids'):
            record = self.env['alert.report.wizard'].browse(data['ids'])
        else:
            record = self.env['alert.report.wizard'].browse(self._context.get('wizard_id'))
        if record.group_by == 'category':
            if record.category_ids:
                categ_ids = record.category_ids
                products = self.env['product.product'].search(
                    [('type', '=', 'product'), ('categ_id.id', 'in', categ_ids.ids)])
            else:
                categ_ids = self.env['product.category'].search([])
                products = self.env['product.product'].search([('type', '=', 'product')])
            locations = self.env['stock.location'].search([('usage', '=', 'internal')])
            values = {}

            for each in categ_ids:
                categories = []
                for product in products:
                    if product.categ_id.id == each.id:
                        if product.same_for_all:
                            if product.reordering_min_qty <= product.qty_available <= product.alert_qty:
                                for loc in locations:
                                    categories.append({'code': product.default_code,
                                                       'name': product.name,
                                                       'avl_qty': product.qty_available,
                                                       'alert_qty': product.alert_qty,
                                                       'reorder_qty': product.reordering_min_qty,
                                                       'category': each.name,
                                                       'location': loc.complete_name})
                        else:
                            for line in product.alert_product_ids:
                                if product.reordering_min_qty <= product.qty_available <= line.alert_qty:
                                    categories.append({'code': product.default_code,
                                                       'name': product.name,
                                                       'avl_qty': product.qty_available,
                                                       'alert_qty': line.alert_qty,
                                                       'reorder_qty': product.reordering_min_qty,
                                                       'category': each.name,
                                                       'location': line.location_id.complete_name})
                    if len(categories) != 0:
                        values[each.name] = categories
            return values

        elif record.group_by == 'location':
            if record.location_ids:
                loc_id = record.location_ids
            else:
                loc_id = self.env['stock.location'].search([('usage', '=', 'internal')])
            products = self.env['product.product'].search([('type', '=', 'product')])
            values = {}
            for each in loc_id:
                locations = []
                for product in products:
                    if product.same_for_all:
                        if product.reordering_min_qty <= product.qty_available <= product.alert_qty:
                            locations.append({'code': product.default_code,
                                              'name': product.name,
                                              'avl_qty': product.qty_available,
                                              'alert_qty': product.alert_qty,
                                              'reorder_qty': product.reordering_min_qty,
                                              'category': product.categ_id.name,
                                              'location': each.complete_name,
                                              })
                    else:
                        for line in product.alert_product_ids:
                            if product.reordering_min_qty <= product.qty_available <= line.alert_qty:
                                if line.location_id.id == each.id:
                                    locations.append({'code': product.default_code,
                                                      'name': product.name,
                                                      'avl_qty': product.qty_available,
                                                      'alert_qty': line.alert_qty,
                                                      'reorder_qty': product.reordering_min_qty,
                                                      'category': product.categ_id.name,
                                                      'location': each.complete_name,
                                                      })
                if len(locations) != 0:
                    values[each.complete_name] = locations
            return values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
