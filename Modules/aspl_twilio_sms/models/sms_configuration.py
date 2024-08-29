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

import requests
from odoo import models, fields, _
from odoo.exceptions import UserError


class SmsConfiguration(models.Model):
    _name = "sms.configuration"
    _rec_name = 'account_sid'
    _description = "SMS Configuration"

    account_sid = fields.Char(string='Account SID', required=True)
    auth_token = fields.Char(string='Auth Token', required=True)
    sms_from = fields.Char(string='SMS From', required=True, help="Sender Number \n Hosting the sms from this number")
    is_active = fields.Selection([('active', 'Enable'), ('archive', 'Disable')], string='Active',
                                 default='active')
    status = fields.Selection([('not_verified', 'Not Verified'), ('verified', 'Verified')], string="Status",
                              default='not_verified')

    def toggle_active(self):
        if not self.is_active and self.status == 'verified' and not any(conf.is_active for conf in self.search([])):
            self.is_active = True
        elif self.is_active:
            self.is_active = False
        else:
            raise UserError(_("Connection is not Verified or Only one connection can be active at a time !!!"))

    def test_connection(self):
        try:
            res = requests.get('https://api.twilio.com/2010-04-01/Accounts.json',
                               auth=(self.account_sid, self.auth_token))
        except requests.ConnectionError:
            raise UserError(_("No Internet Connection !"))
        if res.status_code == 200:
            self.status = 'verified'
            self.env.cr.commit()
            return {
                'name': _('SMS Configuration'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'wizard.connection.notification',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            self.status = 'not_verified'
            self.is_active = False
            self.env.cr.commit()
            raise UserError(_("Connection Test Failed ! \n %s") % res.json().get('detail'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
