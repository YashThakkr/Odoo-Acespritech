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

from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DailyInvoiceReportPdf(models.TransientModel):
    _name = "daily.invoice"
    _description = "Daily Invoice"

    to_date = fields.Date(string="To Date", default=datetime.today().date())
    from_date = fields.Date(string="From Date", default=datetime.today().date())
    customer_ids = fields.Many2many('res.partner',
                                    'daily_invoice_customer_rel',
                                    'daily_inv_id', 'cust_id',
                                    string="Customers")
    sale_team_ids = fields.Many2many('crm.team',
                                     'daily_invoice_crm_team_rel',
                                     'team_daily_inv_id', 'team_id',
                                     string="Sale Teams")

    @api.constrains('from_date')
    def check_date(self):
        if self.from_date > date.today():
            raise ValidationError(_('You Cannot Enter Future date'))

    def action_print(self):
        datas = {
            'id': self.id
        }
        return self.env.ref('aspl_daily_invoice_report_ee.action_report_daily_invoice').report_action(self, data=datas)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
