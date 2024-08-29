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

import logging
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied, ValidationError
from odoo.http import request
import pytz

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    rfid_no = fields.Char('RFID No.')

    @api.constrains('rfid_no')
    def _check_rfid_no(self):
        for record in self:
            if record.rfid_no and self.search([('rfid_no', '=', record.rfid_no), ('id', '!=', record.id)]):
                raise ValidationError(_('User is Already assigned with "%s" RFID number !!') % (record.rfid_no))

    @classmethod
    def _login(cls, db, login, password=None, user_agent_env=None):
        user_id = False
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                user_detail = self.search([('login', '=', login)])
                if user_detail:
                    user_id = user_detail.id
                    if password:
                        with self._assert_can_auth():
                            user = self.search(self._get_login_domain(login))
                            if not user:
                                raise AccessDenied()
                            user = user.with_user(user.id)
                            user._check_credentials(password, user_agent_env)
                            tz = request.httprequest.cookies.get('tz') if request else None
                            if tz in pytz.all_timezones and (not user.tz or not user.login_date):
                                # first login or missing tz -> set tz to browser tz
                                user.tz = tz
                            user._update_last_login()
                    else:
                        user = user_detail.with_user(user_detail.id)
                        user._update_last_login()
        except AccessDenied:
            user_id = False
            ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
            _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
            raise

        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        _logger.info("Login successful for db:%s login:%s from %s %s", db, login, ip, user.id)
        return user.id

    @api.model
    def check_login(self, vals):
        """ Compare user rfid for Login """
        if vals.get('card_no'):
            user_id = self.env['res.users'].sudo().search([('rfid_no', '=', vals.get('card_no'))], limit=1)
            if user_id:
                if user_id.rfid_no == vals.get('card_no'):
                    return {'msg': 'success', 'user_id': int(user_id)}
                else:
                    return {'msg': 'not_match'}
            else:
                return {'msg': 'not_match'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
