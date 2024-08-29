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
from twilio.rest import Client


class SmsGroup(models.Model):
    _name = "sms.group"
    _description = "SMS Group"

    name = fields.Char(string="Name")
    partners_ids = fields.Many2many('res.partner', string="Partner(s)")


class SendSms(models.Model):
    _name = "send.sms"
    _rec_name = 'sms_to'
    _description = "Send SMS"

    sms_to = fields.Selection([('group', 'Group'), ('partners', 'Partners'), ('individual', 'Individual')],
                              string="Send By", default='group')
    partners_ids = fields.Many2many('res.partner', string="Partner(s)")
    group_id = fields.Many2one('sms.group', string="Group")
    mobile = fields.Char(string="Mobile")
    track = fields.Boolean(string="Track")
    message = fields.Text(string="Message")

    def send_sms_action(self, record):
        sms_configuration = self.env['sms.configuration'].search(
            [('status', '=', 'verified'), ('is_active', '=', True)])
        if record and sms_configuration:
            if record.partner_id and record.partner_id.mobile:
                try:
                    client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
                    client.messages.create(to=record.partner_id.mobile.replace(" ", ""),
                                           from_=sms_configuration.sms_from,
                                           body="Hello, %s Your order No. %s" % (record.partner_id.name, record.name))
                except Exception as e:
                    pass

    def send_sms(self):
        sms_configuration = self.env['sms.configuration'].search(
            [('status', '=', 'verified'), ('is_active', '=', 'active')])
        if sms_configuration:
            if self.sms_to == 'individual' and self.mobile:
                try:
                    client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
                    msg = client.messages.create(to=self.mobile.replace(" ", ""), from_=sms_configuration.sms_from,
                                                 body=self.message or '')
                    if self.track:
                        self.env['sms.delivery.report'].create({
                            'sms_to': self.mobile.replace(" ", ""), 'msg_sid': msg.sid,
                            'message': self.message or '', 'date': msg.date_created,
                            'status': client.messages(msg.sid).fetch().status
                        })
                except requests.ConnectionError:
                    raise UserError(_("No Internet Connection !"))
                except ValueError:
                    pass
                except Exception as e:
                    if self.track:
                        self.env['sms.delivery.report'].create({
                            'sms_to': self.mobile.replace(" ", ""),
                            'message': self.message or '', 'status': 'failed',
                            'failed_reason': e
                        })
                    else:
                        raise UserError(_("Error:\n %s") % e)
            elif self.sms_to == 'partners' and self.partners_ids:
                for partner in self.partners_ids.filtered(lambda l: l.mobile):
                    try:
                        client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
                        msg = client.messages.create(to=partner.mobile.replace(" ", ""),
                                                     from_=sms_configuration.sms_from,
                                                     body=self.message or '')
                        if self.track:
                            self.env['sms.delivery.report'].create({
                                'sms_to': partner.mobile.replace(" ", ""), 'msg_sid': msg.sid,
                                'message': self.message or '', 'date': msg.date_created,
                                'status': client.messages(msg.sid).fetch().status
                            })
                    except requests.ConnectionError:
                        raise UserError(_("No Internet Connection !"))
                    except ValueError:
                        pass
                    except Exception as e:
                        if self.track:
                            self.env['sms.delivery.report'].create({
                                'sms_to': partner.mobile.replace(" ", ""),
                                'message': self.message or '', 'status': 'failed',
                                'failed_reason': e
                            })
                        else:
                            raise UserError(_("Error:\n %s") % e)
            elif self.sms_to == 'group' and self.group_id:
                for partner in self.group_id.partners_ids.filtered(lambda l: l.mobile):
                    try:
                        client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
                        msg = client.messages.create(to=partner.mobile.replace(" ", ""),
                                                     from_=sms_configuration.sms_from,
                                                     body=self.message or '')
                        if self.track and client.messages(msg.sid).fetch().status == 'sent':
                            self.env['sms.delivery.report'].create({
                                'sms_to': partner.mobile.replace(" ", ""), 'msg_sid': msg.sid,
                                'message': self.message or '', 'date': msg.date_created,
                                'status': client.messages(msg.sid).fetch().status
                            })
                    except requests.ConnectionError:
                        raise UserError(_("No Internet Connection !"))
                    except ValueError:
                        pass
                    except Exception as e:
                        if self.track:
                            error_msg = self.env['sms.delivery.report'].create({
                                'sms_to': partner.mobile.replace(" ", ""),
                                'message': self.message or '', 'status': 'failed',
                                'failed_reason': e
                            })
                            if 'naive datetime' in error_msg.failed_reason:
                                error_msg.unlink()
                        else:
                            raise UserError(_("Error:\n %s") % e)
        else:
            raise UserError(
                _("Please configure SMS api from settings or change status to Active of verified configuration !"))


class SmsQueue(models.Model):
    _name = 'sms.queue'
    _rec_name = 'mobile'
    _description = "SMS Queue"

    mobile = fields.Char(string="Mobile", required=True)
    message = fields.Text(string="Message", required=True)
    track = fields.Boolean(string="Track")
    status = fields.Selection([('new', 'New'), ('cancel', 'Cancel'), ('executed', 'Executed')], string="Status",
                              default="new")

    def send_queue_sms(self):
        sms_configuration = self.env['sms.configuration'].search(
            [('status', '=', 'verified'), ('is_active', '=', 'active')])
        sms_ids = self.search([('status', '=', 'new')])
        if sms_configuration:
            if sms_ids:
                try:
                    client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
                    for sms in sms_ids:
                        msg = client.messages.create(to=sms.mobile.replace(" ", ""), from_=sms_configuration.sms_from,
                                                     body=sms.message or '')
                        if sms.track:
                            record = self.env['sms.delivery.report'].create({
                                'sms_to': sms.mobile.replace(" ", ""), 'msg_sid': msg.sid,
                                'message': sms.message or '', 'date': msg.date_created,
                                'status': client.messages(msg.sid).fetch().status
                            })
                except requests.ConnectionError:
                    raise UserError(_("No Internet Connection !"))
                except ValueError:
                    pass
                except Exception as e:
                    if sms.track:
                        self.env['sms.delivery.report'].create({
                            'sms_to': sms.mobile.replace(" ", ""),
                            'message': sms.message or '', 'status': 'failed',
                            'failed_reason': e
                        })
                    else:
                        raise UserError(_("Error:\n %s") % e)
                sms.status = 'executed'
        else:
            raise UserError(
                _("Please configure SMS api from settings or change status to Active of verified configuration !"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
