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
from datetime import datetime, date, timedelta

from odoo.http import request
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SubscriberMembershipHistory(models.Model):
    _name = 'subscriber.membership.history'
    _description = 'Membership History'
    _rec_name = 'membership_id'

    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.company)
    branch_id = fields.Many2one('company.branch', string="Branch")
    membership_id = fields.Many2one('product.product', string="Membership")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    active = fields.Boolean("Active")
    fees = fields.Float("Fees")
    subscriber_id = fields.Many2one('res.partner', string="Member")
    gym_plan_ids = fields.Many2many('gym.plan', 'gym_plan_subscriber_membership_rel',
                                    'subscriber_membership_id',
                                    'gym_plan_id', string="Gym Plan")
    invoice_id = fields.Many2one('account.move', string="Invoice")

    def branch_ids(self):
        bids_lst = []
        if request.httprequest.cookies.get('bids'):
            for branch in request.httprequest.cookies.get('bids'):
                if branch.isnumeric():
                    branch_id = request.env['company.branch'].sudo().browse(
                        int(branch))
                    if branch_id.exists():
                        bids_lst.append(int(branch))
        return bids_lst

    @api.onchange('subscriber_id')
    def onchange_subscriber_id(self):
        """
        :return:
        """
        if self.subscriber_id and self.subscriber_id.branch_id:
            self.branch_id = self.subscriber_id.branch_id.id
        else:
            self.branch_id = False

    def check_expiry_days(self):
        membership_ids = self.env['subscriber.membership.history'].search([('subscriber_id', '=',
                                                                            self.subscriber_id.id)])
        expiry_days = self.env['res.config.settings'].get_values()['membership_renewal_days']
        renew_membership_ids = membership_ids.filtered(
            lambda x: x.end_date <= date.today() + timedelta(days=expiry_days))
        if renew_membership_ids == membership_ids:
            return 'renew'
        elif self.invoice_id and self.invoice_id.payment_state != 'paid':
            return 'payment'
        else:
            return False

    @api.depends('invoice_id.payment_state', 'invoice_id')
    def _compute_state(self):
        for each in self:
            if each.invoice_id.payment_state == "paid":
                each.state = "paid"
            elif not each.invoice_id:
                each.state = 'draft'

    state = fields.Selection(
        selection=[('draft', 'Draft'), ('validated', 'Validated'), ('paid', 'Paid'),
                   ('running', 'Running'),
                   ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='draft',
        string="State",
        compute="_compute_state", store=True)

    def create_membership_invoice(self):
        if self.membership_id:
            invoice_lines = [(0, 0, {'name': self.membership_id.name,
                                     'product_id': self.membership_id.id,
                                     'quantity': 1.0,
                                     'branch_id': self.branch_id.id,
                                     'price_unit': self.fees,
                                     'company_id': self.company_id.id
                                     })]
            invoice_obj = self.env['account.move'].sudo().with_context({'default_company_id':
                                                                            self.company_id.id or
                                                                            self.env.company.id})
            invoice_id = invoice_obj.create({'partner_id': self.subscriber_id.id,
                                             'move_type': 'out_invoice',
                                             'branch_id': self.branch_id.id,
                                             'company_id': self.company_id.id,
                                             'invoice_date': date.today(),
                                             'invoice_line_ids': invoice_lines
                                             })
            if invoice_id:
                for each in invoice_id.invoice_line_ids:
                    each.tax_ids = each._get_computed_taxes()

            self.invoice_id = invoice_id.id
            self.invoice_id.action_post()
            self.write({'state': 'validated'})

    @api.model
    def membership_inactive(self):
        memberships = self.env['subscriber.membership.history'].search([])
        for each in memberships:
            each.active = True if date.today() >= each.start_date and date.today() <= each.end_date else False
            if each.end_date <= date.today() + timedelta(days=10):
                each.send_membership_expiry_mail()

    def send_membership_expiry_mail(self):
        if self.subscriber_id.email:
            try:
                template_id = self.env.ref('aspl_fitness_management.send_membership_expiry_mail')

                if template_id:
                    template_id.send_mail(self.id, force_send=True, raise_exception=False)
                    _logger.info('Mail Send to %s' % (self.subscriber_id.name))

            except Exception:
                _logger.warning('Mail Server not Configured', exc_info=True)

    @api.model
    def membership_renewal_reminder(self):
        subscriber_membership_ids = self.env['subscriber.membership.history'].search([])
        renewal_reminder_ids = self.env['membership.renewal.reminder'].search([])
        for each in subscriber_membership_ids:
            reminde_line_ids = renewal_reminder_ids.filtered(lambda x: each.end_date - timedelta(
                days=x.days) == date.today())
            for each_line in reminde_line_ids:
                each_line.send_renewal_reminder_mail(each)

    def action_view_customer_invoice(self):
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'view_id': self.env.ref('account.view_move_form').id,
            'domain': [('id', '=', self.invoice_id.id)]
        }
        return action

    def button_register_gym_payment(self):
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.register',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Register Payment',
            'view_id': self.env.ref('account.view_account_payment_register_form').id,
            'context': {'default_invoice_ids': [(4, self.invoice_id.id, None)],
                        'active_model': 'account.move',
                        'active_ids': self.invoice_id.ids, 'membership_id': self.id}
        }
        return action

    def button_cancel(self):
        self.state = 'cancelled'

    @api.model
    def payment_pending_membership(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                pending_membership = self.search_read(
                    ['&', ('state', '=', 'validated'), '|', ('branch_id', '=', None), ('branch_id', '=', bids_tpl)])
            else:
                bids_tpl = tuple(bids_lst)
                pending_membership = self.search_read(['&', ('state', '=', 'validated'),  '|', ('branch_id', '=', None), ('branch_id', 'in', bids_tpl)])
            for pm in pending_membership:
                pm.update({
                    'currency_symbol': self.env.company.currency_id and
                    self.env.company.currency_id.symbol})
            if pending_membership and pending_membership[0] and pending_membership[0].get('invoice_id'):
                invoice_id = self.env['account.move'].browse(pending_membership[0].get('invoice_id')[0])
            if pending_membership and pending_membership[0] and invoice_id:
                pending_membership[0].update({'amount_due': invoice_id.amount_residual})
            return pending_membership

    @api.model
    def month_wise_collection(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state = 'paid' or state = 'running'" \
                                           " or state = 'completed' and branch_id = {} " \
                                           "or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
            else:
                bids_tpl = tuple(bids_lst)
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state = 'paid' or state = 'running'" \
                                           " or state = 'completed' and branch_id in {} " \
                                           "or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
            membership_ids = self._cr.dictfetchall()
            monthly_collection = []
            current_time = datetime.now()
            for month in range(1,13):
                amount = 0
                for membership_id in membership_ids:
                    if membership_id.get('start_date').strftime('%m') == str(month) \
                            and membership_id.get('start_date').strftime('%Y') == \
                            current_time.strftime('%Y'):
                        amount += int(membership_id.get('fees'))
                monthly_collection.append(amount)
            return [monthly_collection, self.env.company.currency_id and
                    self.env.company.currency_id.symbol]

    @api.model
    def year_wise_collection(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state = 'validated' and branch_id = {} " \
                                           "or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
            else:
                bids_tpl = tuple(bids_lst)
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state = 'validated' and branch_id in {} " \
                                           "or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
            membership_history_ids = self._cr.dictfetchall()
            last_years = []
            yearly_collection = []
            current_year = date.today().year
            for count in range(0,5):
                last_years.insert(0, current_year - count)
            for year in last_years:
                amount = 0
                for membership_id in membership_history_ids:
                    if membership_id.get('start_date').strftime('%Y') == str(year):
                        amount += int(membership_id.get('fees'))
                yearly_collection.append(amount)
            return yearly_collection

    @api.model
    def past_month_collection(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state = 'paid' or state = 'running'" \
                                           " or state = 'completed' and branch_id = {} " \
                                           "or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
            else:
                bids_tpl = tuple(bids_lst)
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state = 'paid' or state = 'running'" \
                                           " or state = 'completed' and branch_id in {} " \
                                           "or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
            membership_history_ids = self._cr.dictfetchall()
            current_time = datetime.now()
            start_date = current_time - timedelta(30)
            amount = 0
            for membership_id in membership_history_ids:
                if membership_id.get('start_date') >= start_date.date():
                    amount += int(membership_id.get('fees'))
            return [amount, self.env.company.currency_id and
                    self.env.company.currency_id.symbol]

    @api.model
    def user_by_branch(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state != 'draft' or state != 'cancelled' and " \
                                           "branch_id = {} or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
            else:
                bids_tpl = tuple(bids_lst)
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state != 'draft' or state != 'cancelled' and " \
                                           "branch_id in {} or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
                bids_lst = sorted(bids_lst)
            membership_history_ids = self._cr.dictfetchall()
            users_by_branch = []
            for branch_id in bids_lst:
                amount = 0
                for membership_id in membership_history_ids:
                    if branch_id == membership_id.get('branch_id'):
                        amount += 1
                users_by_branch.append(amount)
            return users_by_branch

    @api.model
    def user_by_branch_male(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state != 'draft' or state != 'cancelled' and " \
                                           "branch_id = {};".format(bids_tpl)
                self._cr.execute(membership_history_query)
            else:
                bids_tpl = tuple(bids_lst)
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state != 'draft' or state != 'cancelled' and " \
                                           "branch_id in {};".format(bids_tpl)
                self._cr.execute(membership_history_query)
                bids_lst = sorted(bids_lst)
            membership_history_ids = self._cr.dictfetchall()
            users_by_branch_male = []
            for branch_id in bids_lst:
                amount = 0
                for membership_id in membership_history_ids:
                    user_id = membership_id.get('subscriber_id')
                    user = self.env['res.partner'].search_read([('id','=',user_id)])
                    if user and branch_id == membership_id.get('branch_id') \
                            and user[0].get('gender') == 'Male':
                        amount += 1
                users_by_branch_male.append(amount)
            return users_by_branch_male

    @api.model
    def user_by_branch_female(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state != 'draft' or state != 'cancelled' and " \
                                           "branch_id = {};".format(bids_tpl)
                self._cr.execute(membership_history_query)
            else:
                bids_tpl = tuple(bids_lst)
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state != 'draft' or state != 'cancelled' and " \
                                           "branch_id in {};".format(bids_tpl)
                self._cr.execute(membership_history_query)
                bids_lst = sorted(bids_lst)
            membership_history_ids = self._cr.dictfetchall()
            users_by_branch_male = []
            for branch_id in bids_lst:
                amount = 0
                for membership_id in membership_history_ids:
                    user_id = membership_id.get('subscriber_id')
                    user = self.env['res.partner'].search_read([('id','=',user_id)])
                    if user and branch_id == membership_id.get('branch_id') \
                            and user[0].get('gender') == 'Female':
                        amount += 1
                users_by_branch_male.append(amount)
            return users_by_branch_male

    @api.model
    def current_date(self):
        cur_date = date.today()
        return cur_date

    @api.model
    def expiry_alert_date(self):
        expiry_days = self.env['res.config.settings'].get_values()['expiry_alert_days']
        expiry_date = date.today()+timedelta(days=expiry_days)
        return expiry_date

    @api.model
    def expiry_alert_count(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state != 'draft' and branch_id = {} " \
                                           "or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
            else:
                bids_tpl = tuple(bids_lst)
                membership_history_query = "select * from subscriber_membership_history where " \
                                           "active = true and state != 'draft' and branch_id in {} " \
                                           "or branch_id is null;".format(bids_tpl)
                self._cr.execute(membership_history_query)
            membership_history_ids = self._cr.dictfetchall()
            amount = 0
            for membership_id in membership_history_ids:
                if membership_id.get('end_date') >= self.current_date() and \
                        membership_id.get('end_date') <= self.expiry_alert_date():
                    amount += 1
            return amount


class MembershipRenewalReminder(models.Model):
    _name = 'membership.renewal.reminder'
    _description = 'Membership Renewal Reminder'

    name = fields.Char("Name")
    template_id = fields.Many2one('mail.template', string="Template")
    days = fields.Integer("Days")
    branch_id = fields.Many2one('company.branch', string="Branch")

    def send_renewal_reminder_mail(self, subscriber_membership_id):
        if subscriber_membership_id.subscriber_id.email:
            try:
                template_id = self.template_id

                if template_id:
                    template_id.send_mail(subscriber_membership_id.id, force_send=True,
                                          raise_exception=False)
                    _logger.info('Mail Send to %s' % (subscriber_membership_id))

            except Exception:
                _logger.warning('Mail Server not Configured', exc_info=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
