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

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProfitabilityInvoiceReport(models.TransientModel):
    _name = 'profitability.invoice.report'
    _description = "Profitability By Invoice Report"

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    customer_ids = fields.Many2many('res.partner',
                                    'profitability_invoice_customer_rel',
                                    'profitability_inv_id', 'cust_id',
                                    string="Customers")
    product_ids = fields.Many2many('product.product', string="Products")
    sale_team_ids = fields.Many2many('crm.team',
                                     'profitability_invoice_crm_team_rel',
                                     'team_profitability_inv_id', 'team_id',
                                     string="Sale Teams")

    is_show_credit = fields.Boolean(string="Show Credit")
    report_view = fields.Selection([('Summary', 'Summary'), ('Detail', 'Detail')], string="Report View",
                                   default='Summary',required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id,
                                 required=True)

    @api.onchange('to_date')
    def validate_date(self):
        if self.from_date > self.to_date:
            raise UserError(_("To Date Must Be Greater Than From Date"))

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data = {'ids': self.ids,
                'model': 'profitability.invoice.report',
                'form': data
                }
        return self.env.ref('aspl_profitability_invoice_report.action_report_profitability_by_invoice').report_action(self, data=data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
