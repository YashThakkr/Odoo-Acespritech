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


from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MembershipSubscription(models.TransientModel):
    _name = 'membership.subscription'
    _description = 'Membership Subscription'

    def _default_branch(self):
        active_context = self._context.get('active_id')
        subscriber_id = self.env['res.partner'].browse(active_context)

        return subscriber_id.branch_id and \
                         subscriber_id.branch_id.id or False

    branch_id = fields.Many2one('company.branch', string="Branch", default=_default_branch)
    membership_id = fields.Many2one('product.product', string="Membership")
    fees = fields.Float(string="Fees")
    start_date = fields.Date(string="Start Date", default=fields.Date.context_today)
    end_date = fields.Date(string="End Date")

    @api.onchange('start_date', 'membership_id', 'membership_id.membership_period_type',
                  'membership_id.membership_period', 'membership_id.list_price')
    def _onchange_membership_dates(self):
        if self.membership_id:
            if self.start_date:
                membership_days = 0
                if self.membership_id.membership_period_type == 'days':
                    membership_days += self.membership_id.membership_period
                elif self.membership_id.membership_period_type == 'weeks':
                    membership_days += self.membership_id.membership_period * 7
                elif self.membership_id.membership_period_type == 'months':
                    membership_days += self.membership_id.membership_period * 30
                elif self.membership_id.membership_period_type == 'years':
                    membership_days += self.membership_id.membership_period * 365
                self.end_date = self.start_date + timedelta(days=membership_days)
            self.fees = self.membership_id.list_price or 0.0

    @api.constrains('start_date', 'end_date')
    def _check_validity_start_end_date(self):
        for each in self:
            if each.start_date and each.end_date and each.end_date < each.start_date:
                raise ValidationError(_('End date must be greater than start date.'))

    def button_create_membership(self):
        subscriber_id = self.env['res.partner'].browse(self._context.get('active_id'))
        end_date = self.end_date
        if not end_date:
            self._onchange_membership_dates()
        if self.membership_id:
            vals = {'subscriber_id': subscriber_id.id,
                    'branch_id': self.branch_id.id,
                    'company_id': self.branch_id.company_id.id,
                    'membership_id': self.membership_id.id,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'active': True,
                    'fees': self.fees
                    }
            self.env['subscriber.membership.history'].create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
