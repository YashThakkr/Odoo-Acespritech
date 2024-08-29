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

import base64
import io
from odoo import fields as odoo_fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class PortalPayment(CustomerPortal):
    _items_per_page = 20

    def _get_archive_groups(self, model, domain=None, fields=None, groupby="create_date", order="create_date desc"):
        if not model:
            return []
        if domain is None:
            domain = []
        if fields is None:
            fields = ['name', 'create_date']
        groups = []
        # for group in request.env[model]._read_group_raw(domain, fields=fields, groupby=groupby, orderby=order):
        for group in request.env[model].read_group(domain, fields, groupby, orderby=order):
            # dates, label = group[groupby]
            label = group[groupby]
            # date_begin, date_end = dates.split('/')
            date_begin = group['__range'][groupby]['from']
            date_end = group['__range'][groupby]['to']
            groups.append({
                'date_begin': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_begin)),
                'date_end': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_end)),
                'name': label,
                'item_count': group[groupby + '_count']
            })
        return groups

    def _prepare_portal_layout_values(self):
        values = super(PortalPayment, self)._prepare_portal_layout_values()
        payment_count = request.env['account.payment'].sudo().search_count([])
        values['payment_count'] = payment_count
        return values

    @http.route(['/my/payment', '/my/payment/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payment(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        AccountPayment = request.env['account.payment']

        domain = []

        searchbar_sortings = {
            'date': {'label': _('Payment Date'), 'order': 'date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('account.move', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        payment_count = AccountPayment.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/payment",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=payment_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        payments = AccountPayment.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_payment_history'] = payments.ids[:100]

        values.update({
            'date': date_begin,
            'payments': payments,
            'page_name': 'Payment',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/payment',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("aspl_website_account_payment_ee.portal_my_payment", values)

    def _payment_get_page_view_values(self, payment, access_token, **kwargs):
        values = {
            'page_name': 'Payment',
            'payment': payment,
        }
        return self._get_page_view_values(payment, access_token, values, 'my_payment_history', False, **kwargs)

    def _get_page_view_values(self, document, access_token, values, session_history, no_breadcrumbs, **kwargs):
        if access_token:
            # if no_breadcrumbs = False -> force breadcrumbs even if access_token to `invite` users to register if they click on it
            values['no_breadcrumbs'] = no_breadcrumbs
            values['access_token'] = access_token
            values['token'] = access_token  # for portal chatter

        # Those are used notably whenever the payment form is implied in the portal.
        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']
        # Email token for posting messages in portal view with identified author
        if kwargs.get('pid'):
            values['pid'] = kwargs['pid']
        if kwargs.get('hash'):
            values['hash'] = kwargs['hash']

        history = request.env['account.payment'].sudo().search([]).ids
        values.update(self.get_records_pager(history, document))
        return values

    def get_records_pager(self, ids, current):
        if current.id in ids and (hasattr(current, 'website_url') or hasattr(current, 'access_url')):
            attr_name = 'access_url' if hasattr(current, 'access_url') else 'website_url'
            idx = ids.index(current.id)
            return {
                'prev_record': idx != 0 and current.browse(ids[idx - 1]).id,
                'next_record': idx < len(ids) - 1 and current.browse(ids[idx + 1]).id,
            }
        return {}

    @http.route(['/my/payment/<int:payment_id>'], type='http', auth="public", website=True)
    def portal_my_payment_detail(self, payment_id, access_token=None, report_type=None, download=False, **kw):
        try:
            payment_sudo = self._document_check_access('account.payment', payment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=payment_sudo, report_type=report_type, report_ref='account.action_report_payment_receipt',
                                     download=download)

        values = self._payment_get_page_view_values(payment_sudo, access_token, **kw)
        acquirers = values.get('acquirers')
        if acquirers:
            country_id = values.get('partner_id') and values.get('partner_id')[0].country_id.id
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(payment_sudo.amount,
                                                                         payment_sudo.currency_id, country_id)

        return request.render("aspl_website_account_payment_ee.portal_payment_page", values)

    @http.route(['/attachment/download',], type='http', auth='public')
    def download_attachment(self, attachment_id):
        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search([('id', '=', int(attachment_id))])

        if attachment:
            attachment = attachment[0]
        else:
            return request.redirect('/my')

        if attachment["type"] == "url":
            if attachment["url"]:
                return request.redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
            return http.send_file(data, filename=attachment['name'], as_attachment=True)
        else:
            return request.not_found()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
