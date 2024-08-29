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

from odoo.http import route, request
from odoo.addons.web.controllers.main import content_disposition
from odoo.tools import html_escape
from odoo import http
import odoo.addons.web.controllers.main as main
import json
from werkzeug.urls import url_decode
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from werkzeug.datastructures import Headers


class ReportController(http.Controller):

    @http.route(['/write/rating'], type='json', auth="public", methods=['POST'], website=True,csrf=False,
                multilang=False)
    def write_rating(self, float_rating, partner):
        print("\n\n\n\n kwargs ----------->>>>>>>>>>>>", float_rating, partner)
        # self.float_rating = args.get('float_rating')
        partner_id = request.env['res.partner'].browse(int(partner))
        partner_id.sudo().write({'float_rating': float_rating})

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
