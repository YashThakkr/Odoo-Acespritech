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

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, \
    get_records_pager

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class NutritionPortalAccount(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(NutritionPortalAccount, self)._prepare_portal_layout_values()
        user = request.env['res.users'].browse(request.session.uid)
        domain = [('plan_type', 'in', ['nutrition', 'both'])] if request.env.user.has_group(
            'base.group_erp_manager') else \
            [('subscriber_id', '=', user.partner_id.id), ('plan_type', 'in', ['nutrition', 'both'])]
        nutrition_plan_count = request.env['subscriber.plan'].search_count(domain)
        values['nutrition_plan_count'] = nutrition_plan_count
        return values

    @http.route(['/my/nutrition_plans', '/my/nutrition_plans/page/<int:page>'], type='http',
                auth="user", website=True)
    def nutrition_subscriber_plan(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        nutrition_plans = request.env['subscriber.plan']
        user = request.env['res.users'].browse(request.session.uid)
        domain = [] if request.env.user.has_group('base.group_erp_manager') else [
            ('subscriber_id', '=', user.partner_id.id)]

        nutrition_plan_count = nutrition_plans.search_count(domain)
        pager = portal_pager(
            url="/my/nutrition_plans",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=nutrition_plan_count,
            page=page,
            step=self._items_per_page
        )
        nutrition_plans = nutrition_plans.search(domain, limit=self._items_per_page,
                                                 offset=pager['offset'])
        request.session['nutrition_plans_history'] = nutrition_plans.ids[:100]

        values.update({
            'date': date_begin,
            'nutrition_plans': nutrition_plans,
            'page_name': 'nutrition_plans',
            'pager': pager,
            'default_url': '/my/nutrition_plans',
            'sortby': sortby,
        })
        return request.render("aspl_fitness_management_ee.portal_my_nutrition_plans", values)

    def _nutrition_plan_get_page_view_values(self, nutrition_plan, access_token, **kwargs):
        values = {
            'page_name': 'nutrition_plan',
            'nutrition_plan': nutrition_plan,
        }
        return self._get_page_view_values(nutrition_plan, access_token, values,
                                          'nutrition_plans_history', False, **kwargs)

    @http.route(['/my/nutrition_plans/<int:nutrition_plan_id>'], type='http', auth="public",
                website=True)
    def portal_my_nutrition_plan_detail(self, nutrition_plan_id, access_token=None,
                                        report_type=None, download=False, **kw):
        try:
            nutrition_plan_sudo = self._document_check_access('subscriber.plan',
                                                              nutrition_plan_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._nutrition_plan_get_page_view_values(nutrition_plan_sudo, access_token, **kw)
        values.update(get_records_pager(request.session.get('nutrition_plans_history', []),
                                        nutrition_plan_sudo))
        return request.render("aspl_fitness_management_ee.portal_nutrition_plan_page3", values)

    @http.route('/my/nutrition_plans/<int:nutrition_plan_id>/report', auth="public", type='http',
                website=True)
    def get_nutrition_print_report(self, nutrition_plan_id, model="subscriber.plan"):
        nutrition_plan_obj = request.env[model].browse([int(nutrition_plan_id)])

        domain = [('id', '=', int(nutrition_plan_id))]
        Model = request.env[model].sudo()
        try:
            record = Model.search_read(domain, 0, False, False)
        except Exception as e:
            pass
        data = nutrition_plan_obj.read()[0]
        datas = {
            'ids': int(nutrition_plan_id),
            'model': nutrition_plan_obj._name,
            'form': data,
        }
        report_id = request.env.ref('aspl_fitness_management_ee.nutrition_plan_schedule_report')
        pdf = report_id.sudo()._render_qweb_pdf([int(nutrition_plan_id)], data=datas)[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment'),
            ('target', '_blank'),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
