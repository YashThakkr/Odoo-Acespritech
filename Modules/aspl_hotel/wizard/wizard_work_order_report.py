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

from odoo import api, models, fields


class WizardWorkOrderReport(models.Model):
    _name='wizard.work.order.report'
    _description = "Wizard Work Order Report"

    start_date = fields.Date(string='Start Date',  default=fields.Date.context_today)
    end_date = fields.Date(string='End Date',  default=fields.Date.context_today)
    user_id = fields.Many2many('res.users', string='User')

    def print_report(self):
        datas = {'ids': self._ids,
                 'model': 'wizard.work.order.report',
                 'form': self.read()[0]}
        return self.env.ref('aspl_hotel.action_work_order_report').report_action(self, data=datas)

