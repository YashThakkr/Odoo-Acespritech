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

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
from odoo.models import check_method_name
from odoo.api import call_kw
from odoo.http import request


class MultiBranchPortalAccount(CustomerPortal):

    def _call_kw(self, model, method, args, kwargs):
        check_method_name(method)
        return call_kw(request.env[model], method, args, kwargs)

    @http.route('/check_multi_branch', type='json', auth="user")
    def call(self, model, method, args, domain_id=None, context_id=None):
        return self._call_kw(model, method, args, {})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: