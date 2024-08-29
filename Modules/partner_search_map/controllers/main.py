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

import json
from odoo import http
from odoo.http import request


class WebsiteSale(http.Controller):

    @http.route(['/get_api_key'], type='http', auth="public")
    def get_api_key(self, **post):
        return json.dumps({'key': request.env['ir.config_parameter'].sudo().get_param(
            'partner_search_map.google_api_key') or ''})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
