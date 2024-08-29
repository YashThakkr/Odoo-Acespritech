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

from datetime import datetime
import pytz
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from twilio.rest import Client


class SmsDeliveryReport(models.Model):
    _name = "sms.delivery.report"
    _rec_name = 'sms_to'
    _order = 'id desc'
    _description = "SMS Delivery Report"

    sms_to = fields.Char(string="To")
    msg_sid = fields.Char(string="Message SID")
    message = fields.Text(string="Message")
    date = fields.Datetime(string="Date")
    status = fields.Selection([('accepted', 'Accepted'), ('queued', 'Queued'), ('sending', 'Sending'), ('sent', 'Sent'),
                               ('delivered', 'Delivered'), ('failed', 'Failed'), ('undelivered', 'Undelivered')],
                              string="Status")
    failed_reason = fields.Text(string="Reason")

    def check_delivery_status(self):
        sms_ids = self.search([('status', 'in', ['sent', 'failed']), ('msg_sid', '!=', False)])
        sms_configuration = self.env['sms.configuration'].search(
            [('status', '=', 'verified'), ('is_active', '=', True)])
        try:
            client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
            for sms in sms_ids:
                msg = client.messages(sms.msg_sid).fetch()
                if msg.status != sms.status and msg.status not in ['failed', 'undelivered']:
                    sms.write({'status': msg.status, 'date': msg.date_updated})
                elif msg.status != sms.status and msg.status in ['failed', 'undelivered']:
                    sms.write({'status': msg.status, 'date': msg.date_updated, 'failed_reason': msg.error_message})
        except Exception as e:
            pass

    def retry_sms(self):
        sms_configuration = self.env['sms.configuration'].search(
            [('status', '=', 'verified'), ('is_active', '=', True)])
        if self.sms_to and self.status == 'failed' and sms_configuration:
            try:
                client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
                msg = client.messages.create(to=self.sms_to.replace(" ", ""), from_=sms_configuration.sms_from,
                                             body=self.message or '')
                self.write({'msg_sid': msg.sid, 'date': msg.date_created,
                            'status': client.messages(msg.sid).fetch().status, 'failed_reason': ''})
            except requests.ConnectionError:
                raise UserError(_("No Internet Connection !"))
            except Exception as e:
                raise UserError(_("Error:\n %s") % e)


class ScheduleSms(models.Model):
    _name = "schedule.sms"
    _rec_name = 'sms_to'
    _description = "Schedule SMS"

    sms_to = fields.Selection([('group', 'Group'), ('partners', 'Partners'), ('individual', 'Individual')],
                              string="To", default='group')
    partners_ids = fields.Many2many('res.partner', string="Partner(s)")
    group_id = fields.Many2one('sms.group', string="Group")
    mobile = fields.Char(string="Mobile")
    track = fields.Boolean(string="Track")
    message = fields.Text(string="Message")
    date = fields.Date(string="Date")
    hour = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
                             ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'),
                             ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'),
                             ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24')], string="Hour")
    status = fields.Selection([('new', 'New'), ('cancel', 'Cancel'), ('executed', 'Executed')], string="Status",
                              default="new")

    @api.model
    def send_sms(self):
        sms_configuration = self.env['sms.configuration'].search(
            [('status', '=', 'verified'), ('is_active', '=', 'active')])
        sms_ids = self.env['schedule.sms'].search([('status', '=', 'new'), ('date', '<=', datetime.now(pytz.timezone(self.env.user.tz)).date())])
        ('hour', '<=', str(datetime.now(pytz.timezone(self.env.user.tz)).hour))
        if sms_configuration:
            for sms in sms_ids:
                if int(sms.hour) <= datetime.now().hour:
                    if sms.sms_to == 'individual' and sms.mobile:
                        try:
                            client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
                            msg = client.messages.create(to=sms.mobile.replace(" ", ""),
                                                         from_=sms_configuration.sms_from,
                                                         body=sms.message or '')
                            if sms.track:
                                self.env['sms.delivery.report'].create({
                                    'sms_to': sms.mobile.replace(" ", ""), 'msg_sid': msg.sid,
                                    'message': sms.message or '', 'date': msg.date_created,
                                    'status': client.messages(msg.sid).fetch().status
                                })
                        except requests.ConnectionError:
                            pass
                        except ValueError:
                            pass
                        except Exception as e:
                            if sms.track:
                                self.env['sms.delivery.report'].create({
                                    'sms_to': sms.mobile.replace(" ", ""),
                                    'message': sms.message or '', 'status': 'failed',
                                    'failed_reason': e
                                })
                        sms.status = 'executed'
                    elif sms.sms_to == 'partners' and sms.partners_ids:
                        for partner in sms.partners_ids.filtered(lambda l: l.mobile):
                            try:
                                client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
                                msg = client.messages.create(to=partner.mobile.replace(" ", ""),
                                                             from_=sms_configuration.sms_from,
                                                             body=sms.message or '')
                                if sms.track:
                                    self.env['sms.delivery.report'].create({
                                        'sms_to': partner.mobile.replace(" ", ""), 'msg_sid': msg.sid,
                                        'message': sms.message or '', 'date': msg.date_created,
                                        'status': client.messages(msg.sid).fetch().status
                                    })
                            except requests.ConnectionError:
                                pass
                            except ValueError:
                                pass
                            except Exception as e:
                                if sms.track:
                                    self.env['sms.delivery.report'].create({
                                        'sms_to': partner.mobile.replace(" ", ""),
                                        'message': sms.message or '', 'status': 'failed',
                                        'failed_reason': e
                                    })
                        sms.status = 'executed'
                    elif sms.sms_to == 'group' and sms.group_id:
                        for partner in sms.group_id.partners_ids.filtered(lambda l: l.mobile):
                            try:
                                client = Client(sms_configuration.account_sid, sms_configuration.auth_token)
                                msg = client.messages.create(to=partner.mobile.replace(" ", ""),
                                                             from_=sms_configuration.sms_from,
                                                             body=sms.message or '')
                                if sms.track:
                                    self.env['sms.delivery.report'].create({
                                        'sms_to': partner.mobile.replace(" ", ""), 'msg_sid': msg.sid,
                                        'message': sms.message or '', 'date': msg.date_created,
                                        'status': client.messages(msg.sid).fetch().status
                                    })
                            except requests.ConnectionError:
                                pass
                            except ValueError:
                                pass
                            except Exception as e:
                                if sms.track:
                                    self.env['sms.delivery.report'].create({
                                        'sms_to': partner.mobile.replace(" ", ""),
                                        'message': sms.message or '', 'status': 'failed',
                                        'failed_reason': e
                                    })
                        sms.status = 'executed'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
