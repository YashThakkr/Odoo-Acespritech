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

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalAccount(CustomerPortal):

    @http.route(['/my/invoices/<int:invoice>/accept'], type='json', auth="public", website=True)
    def portal_invoice_accept(self, invoice, access_token=None, name=None, signature=None):
        '''Accepts/ Generates access token and updates invoice with signature.'''
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            invoice = self._document_check_access('account.move', invoice, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            invoice.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('account.account_invoices', [invoice.id])[0]

        _message_post_helper(
            'account.move', invoice.id, _('Invoice signed by %s') % (name,),
            attachments=[('%s.pdf' % invoice.name, pdf)],
            **({'token': access_token} if access_token else {})
        )
        query_string = '&message=sign_ok'
        if invoice.signature:
            query_string += '#allow_payment=yes'
        return {
            'force_refresh': True,
            'redirect_url': invoice.get_portal_url(query_string=query_string),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: