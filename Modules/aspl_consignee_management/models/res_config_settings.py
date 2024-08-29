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

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_create_location = fields.Boolean(string="Create Consignee Location")
    is_create_sale_order = fields.Boolean(string="Create Sales Order as Confirm")
    is_send_mail = fields.Boolean(string="Send Mail Notification on Sale Order Create")
    is_send_mail_request = fields.Boolean(string="Send Mail on Request of Transfer")
    is_send_mail_confirm = fields.Boolean(string="Send Mail on Confirmed of Transfer")
    is_on_consume_item_import = fields.Boolean(string="Create SO On Consume Item Import")
    is_send_alert_for_product_expired = fields.Boolean(
        string="Send Alert for Product Expire to Consignee")
    days = fields.Integer(string="Days")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        conf = self.env['ir.config_parameter']
        res.update(
            is_create_location=conf.get_param('aspl_consignee_management.is_create_location'),
            is_create_sale_order=conf.get_param('aspl_consignee_management.is_create_sale_order'),
            is_send_mail=conf.get_param('aspl_consignee_management.is_send_mail'),
            is_send_mail_request=conf.get_param('aspl_consignee_management.is_send_mail_request'),
            is_send_mail_confirm=conf.get_param('aspl_consignee_management.is_send_mail_confirm'),
            is_on_consume_item_import=conf.get_param(
                'aspl_consignee_management.is_on_consume_item_import'),
            is_send_alert_for_product_expired=conf.get_param('aspl_consignee_management.'
                                                             'is_send_alert_for_product_expired'),
            days=int(conf.get_param('aspl_consignee_management.days'))
        )
        return res

    def set_values(self):
        self.ensure_one()
        super(ResConfigSettings, self).set_values()
        conf = self.env['ir.config_parameter']
        conf.set_param('aspl_consignee_management.is_create_location', self.is_create_location)
        conf.set_param('aspl_consignee_management.is_create_sale_order', self.is_create_sale_order)
        conf.set_param('aspl_consignee_management.is_send_mail', self.is_send_mail)
        conf.set_param('aspl_consignee_management.is_send_mail_request', self.is_send_mail_request)
        conf.set_param('aspl_consignee_management.is_send_mail_confirm', self.is_send_mail_confirm)
        conf.set_param('aspl_consignee_management.is_on_consume_item_import',
                       self.is_on_consume_item_import)
        conf.set_param('aspl_consignee_management.is_send_alert_for_product_expired',
                       self.is_send_alert_for_product_expired)
        conf.set_param('aspl_consignee_management.days', int(self.days))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
