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

from odoo import api, fields, models, _

from odoo.exceptions import UserError


class WizardSms(models.TransientModel):
    _name = 'wizard.sms'
    _description = "Wizard SMS"

    sms_to = fields.Char(string="To")
    message = fields.Text(string="Message")
    track = fields.Boolean(string="Track")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardSms, self).default_get(fields_list)
        if self.env.context.get('active_id') and self.env.context.get('active_model'):
            order = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))
            if order and order.partner_id and order.partner_id.mobile:
                res.update({
                    'sms_to': order.partner_id.mobile
                })
        return res

    def send_wizard_sms(self):
        if self.sms_to and self.message:
            try:
                self.env['sms.queue'].create({'mobile': self.sms_to.replace(" ", ""), 'message': self.message or '',
                                              'track': self.track})
            except Exception as e:
                raise UserError(_("Error:\n %s") % e)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
