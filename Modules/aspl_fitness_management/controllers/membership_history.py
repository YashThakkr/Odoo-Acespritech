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

from datetime import date, timedelta

from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo import http
from odoo.http import request


class GymMembershipPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(GymMembershipPortal, self)._prepare_portal_layout_values()
        user = request.env['res.users'].browse(request.session.uid)
        domain = [('active', '=', True)] if request.env.user.has_group(
            'base.group_erp_manager') else [
            ('subscriber_id', '=', user.partner_id.id), ('active', '=', True)]
        gym_membership_count = request.env['subscriber.membership.history'].search_count(domain)
        values['gym_membership_count'] = gym_membership_count
        return values

    @http.route(['/my/active_memberships', '/my/active_memberships/page/<int:page>'], type='http',
                auth="user",
                website=True)
    def subscriber_memberships(self, page=1, sortby=None, **post):
        values = self._prepare_portal_layout_values()
        membership_ids = request.env['subscriber.membership.history']
        user = request.env['res.users'].browse(request.session.uid)
        domain = [('active', '=', True)] if request.env.user.has_group(
            'base.group_erp_manager') else [
            ('subscriber_id', '=', user.partner_id.id), ('active', '=', True)]
        gym_membership_count = membership_ids.search_count(domain)
        pager = request.website.pager(url="/my/active_memberships", total=gym_membership_count,
                                      page=page, step=20,
                                      scope=7, url_args=post)
        active_memberships = membership_ids.search(domain, limit=gym_membership_count,
                                                   offset=(page - 1) * 10)
        request.session['gym_membership_history'] = active_memberships.ids[:100]

        values.update({
            'active_memberships': active_memberships,
            'page_name': 'active_memberships',
            'pager': pager,
            'default_url': '/my/active_memberships',
            'sortby': sortby,
        })
        return request.render("aspl_fitness_management.portal_my_gym_memberships", values)

    @http.route('/my/active_memberships/<int:membership>/renew_membership', type='http',
                auth='public', website=True,
                csrf=False)
    def renew_gym_membership(self, membership, model="subscriber.membership.history"):
        membership_id = request.env[model].browse([int(membership)])
        membership_ids = request.env[model].search(
            [('subscriber_id', '=', membership_id.subscriber_id.id)])
        expiry_days = request.env['res.config.settings'].sudo().get_values()[
            'membership_renewal_days']
        renew_membership_ids = membership_ids.filtered(
            lambda x: x.end_date <= date.today() + timedelta(days=expiry_days))
        if renew_membership_ids:
            max_ending_date = max(renew_membership_ids.mapped('end_date'))
            if max_ending_date:
                previous_membership_id = renew_membership_ids.filtered(
                    lambda x: x.end_date == max_ending_date)
                if previous_membership_id:
                    date_timedelta = previous_membership_id.end_date - previous_membership_id.start_date
                    start_date = max_ending_date + timedelta(days=1)
                    end_date = start_date + timedelta(days=date_timedelta.days)
                    if renew_membership_ids == membership_ids:
                        copied_vals = membership_id.copy_data({
                            'start_date': start_date,
                            'end_date': end_date,
                            'state': 'draft',
                            'invoice_id': False
                        })[0]
                        new_membership_id = request.env[model].sudo().create(copied_vals)
                        new_membership_id.sudo().create_membership_invoice()
                        new_membership_id.sudo().write({'state': 'validated'})
                        return request.redirect(
                            new_membership_id.invoice_id.get_portal_url(anchor='portal_pay'))
                    elif membership_id.sudo().invoice_id.payment_state != 'paid':
                        return request.redirect(
                            membership_id.invoice_id.get_portal_url(anchor='portal_pay'))

        elif membership_id.sudo().invoice_id.payment_state != 'paid':
            return request.redirect(
                membership_id.invoice_id.get_portal_url(anchor='portal_pay'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
