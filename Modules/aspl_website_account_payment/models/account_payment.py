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

import uuid
from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    access_url = fields.Char(
        'Portal Access URL', compute='_compute_access_url',
        help='Customer Portal URL')
    access_token = fields.Char('Security Token', copy=False)

    def _compute_access_url(self):
        for record in self:
            record.access_url = '#'

    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        url = '/my/payment/' + str(self.id) + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url

    def _portal_ensure_token(self):
        if not self.access_token:
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token

    def _get_report_base_filename(self):
        return self._get_move_display_name()

    def _get_move_display_name(self, show_ref=False):
        self.ensure_one()
        draft_name = ''
        if not self.name or self.name == '/':
            draft_name += ' (* %s)' % str(self.id)
        else:
            draft_name += ' ' + self.name
        return (draft_name or self.name)

    def _get_invoice_payment_amount(self, inv):
        """
        Computes the amount covered by the current payment in the given invoice.

        :param inv: an invoice object
        :returns: the amount covered by the payment in the invoice
        """
        self.ensure_one()
        print("\n\n\n\n inv", inv)
        print("\n\n\n\n self", self)
        return sum([
            data['amount']
            for data in inv._get_reconciled_payments()
            if data['account_payment_id'] == self.id
        ])
