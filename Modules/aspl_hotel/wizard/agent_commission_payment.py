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

from odoo.exceptions import UserError
from odoo import models, fields, api, _


class AgentCommissionPayment(models.TransientModel):
    _name = 'agent.commission.payment'
    _description = 'Agent Commission Payment Report'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    agent_ids = fields.Many2many('res.partner', string='Agent', domain="[('is_agent', '=', True)]")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reserved', 'Reserved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ],string='State')

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise UserError(_('End Date should be greater than Start Date.'))

    def print_report(self):
        data_filter = []
        if self.start_date:
            data_filter = [('commission_date', '>=', self.start_date)]
        if self.end_date:
            data_filter.append(('commission_date', '<=', self.end_date))
        if self.agent_ids:
            data_filter.append(('agent_id', 'in', self.agent_ids.ids))
        if self.state:
            data_filter.append(('state', '=', self.state))
        commission_ids = self.env['agent.commission'].search(data_filter)
        data = {}
        data_new = {}
        if not commission_ids:
            raise UserError(_("There is no any record's are available..!!"))
        for commission in commission_ids:
            if commission.agent_id.id not in data:
                data[commission.agent_id.id] = [{'name': commission.agent_id.name,
                                             'source_document': commission.name,
                                             'date': commission.commission_date,
                                             'amount': commission.amount,
                                             'state': commission.state}]
            else:
                data[commission.agent_id.id].append({'name': commission.agent_id.name,
                                                 'source_document': commission.name,
                                                 'date': commission.commission_date,
                                                 'amount': commission.amount,
                                                 'state': commission.state})
        data_new.update({'commission': data})
        return self.env.ref('aspl_hotel.agent_payment_report').report_action(self, data=data_new)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: