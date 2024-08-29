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

from odoo.addons.portal.controllers.portal import CustomerPortal, get_records_pager

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class GymPortalAccount(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(GymPortalAccount, self)._prepare_portal_layout_values()
        user = request.env['res.users'].browse(request.session.uid)
        domain = [('plan_type', 'in', ['gym', 'both'])] if request.env.user.has_group(
            'base.group_erp_manager') else [
            ('subscriber_id', '=', user.partner_id.id), ('plan_type', 'in', ['gym', 'both'])]
        gym_plan_count = request.env['subscriber.plan'].search_count(domain)
        values['gym_plan_count'] = gym_plan_count
        return values

    @http.route(['/my/gym_plans', '/my/gym_plans/page/<int:page>'], type='http', auth="user",
                website=True)
    def subscriber_plan(self, page=1, sortby=None, **post):
        values = self._prepare_portal_layout_values()
        gym_plan_ids = request.env['subscriber.plan']
        user = request.env['res.users'].browse(request.session.uid)
        domain = [] if request.env.user.has_group('base.group_erp_manager') else [
            ('subscriber_id', '=', user.partner_id.id)]
        gym_plan_count = gym_plan_ids.search_count(domain)
        pager = request.website.pager(url="/my/gym_plans", total=gym_plan_count, page=page, step=10,
                                      scope=7,
                                      url_args=post)
        gym_plans = gym_plan_ids.search(domain, limit=gym_plan_count, offset=(page - 1) * 10)
        request.session['gym_plans_history'] = gym_plans.ids[:100]

        values.update({
            'gym_plans': gym_plans,
            'page_name': 'gym_plans',
            'pager': pager,
            'default_url': '/my/gym_plans',
            'sortby': sortby,
        })
        return request.render("aspl_fitness_management.portal_my_gym_plans", values)

    def _gym_plan_get_page_view_values(self, plan, access_token, **kwargs):
        values = {
            'page_name': 'gym_plans',
            'plan': plan,
        }
        return self._get_page_view_values(plan, access_token, values, 'gym_plans_history', False,
                                          **kwargs)

    @http.route(['/my/gym_plans/<int:gym_plan_id>'], type='http', auth="public", website=True)
    def portal_my_gym_plan_detail(self, gym_plan_id, access_token=None, report_type=None,
                                  download=False, **kw):
        try:
            gym_plan_sudo = self._document_check_access('subscriber.plan', gym_plan_id,
                                                        access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._gym_plan_get_page_view_values(gym_plan_sudo, access_token, **kw)
        values.update(
            get_records_pager(request.session.get('gym_plans_history', []), gym_plan_sudo))
        return request.render("aspl_fitness_management.portal_gym_plan_page3", values)

    @http.route('/my/gym_plans/<int:plan>/report',
                auth="public", type='http', website=True)
    def get_gym_print_report(self, plan, model="subscriber.plan"):
        gym_plan_obj = request.env[model].browse([int(plan)])

        domain = [('id', '=', int(plan))]
        Model = request.env[model].sudo()
        try:
            record = Model.search_read(domain, 0, False, False)
        except Exception as e:
            pass
        data = gym_plan_obj.read()[0]
        datas = {
            'ids': int(plan),
            'model': gym_plan_obj._name,
            'form': data,
        }
        report_id = request.env.ref(
            'aspl_fitness_management.gym_plan_schedule_report')
        pdf = report_id.sudo()._render_qweb_pdf([int(plan)], data=datas)[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment'),
            ('target', '_blank'),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
