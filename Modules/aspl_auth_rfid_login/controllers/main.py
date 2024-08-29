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

import odoo
from odoo import http
from odoo.http import request
# from odoo.addons.web.controllers.main import Home, ensure_db
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.utils import ensure_db
from odoo.tools.translate import _


class Home(Home):

    @http.route(['/check_email_user'], type='json', auth="none", sitemap=False)
    def check_email_user(self, email):
        if email:
            user_id = request.env['res.users'].sudo().search([('login', 'like', email)])
            if user_id:
                return {'user_id': user_id}
        return {'user_id': False}

    @http.route(['/check_user'], type='json', auth="none", sitemap=False)
    def check_user(self, **kw):
        if kw:
            user_detail = request.env['res.users'].sudo().check_login(kw)
            return user_detail

    @http.route()
    def web_login(self, redirect=None, **kw):
        ensure_db()
        # request.para
        # ms['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.update_env:
            # request.uid = odoo.SUPERUSER_ID
            request.update_env = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.update_env
            try:
                if kw.get('msg') and kw.get('msg') == 'success' and kw.get('user_id'):
                    if not request.update_env:
                        request.update_env = odoo.SUPERUSER_ID
                    user = request.env['res.users'].sudo().browse(int(kw.get('user_id')))
                    uid = request.session.authenticate(request.session.db, user.login, False)
                    request.params['login_success'] = True
                    request.params['password'] = False
                    # return request.redirect(self._login_redirect(uid, redirect=redirect))
                    return request.redirect(self._login_redirect(uid, redirect='/web'))
                if kw.get('msg') and kw.get('msg') == 'not_match':
                    values['error'] = _("Wrong login/password")
                    request.params['login_success'] = False
                    return request.render('web.login', values)
                else:
                    uid = request.session.authenticate(request.session.db, request.params['login'],
                                                       request.params['password'])
                    request.params['login_success'] = True
                    return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.update_env = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
