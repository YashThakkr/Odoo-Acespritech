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


class ProfitabilityCustomerReport(models.TransientModel):
    _name = 'profitability.customer.report'
    _description = "Profitability By Customer Report"

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    customer_ids = fields.Many2many('res.partner',
                                    'profitability_customer_customer_rel',
                                    'profitability_cust_id', 'cust_id',
                                    string="Customers")
    sale_team_ids = fields.Many2many('crm.team',
                                     'profitability_customer_crm_team_rel',
                                     'team_profitability_cust_id', 'team_id',
                                     string="Sale Teams")

    is_show_credit = fields.Boolean(string="Show Credit")
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
                'model': 'profitability.customer.report',
                'form': data
                }
        return self.env.ref('aspl_profitability_customer_report.action_report_profitability_by_customer').report_action(self, data=data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
