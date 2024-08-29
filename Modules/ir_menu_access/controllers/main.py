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

import jinja2
import json
import os
import sys
import werkzeug.utils
import werkzeug.wrappers

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.web.controllers import home as web_home


if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.web', "views")

env = jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps


# ----------------------------------------------------------
# Odoo Web web Controllers
# ----------------------------------------------------------
class Home(web_home.Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)
        request.update_env(user=request.session.uid)
        context = request.env['ir.http'].sudo().with_context(
            {'skip_access': 1}).webclient_rendering_context()
        request.env['ir.ui.menu'].sudo().clear_caches()
        request.env['ir.ui.menu'].sudo().load_menus(request.session.debug)

        return request.render('web.webclient_bootstrap', qcontext=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
