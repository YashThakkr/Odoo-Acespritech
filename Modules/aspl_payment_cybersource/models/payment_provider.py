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

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Paymentprovider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('cybersource', 'CyberSource')], ondelete={'cybersource': 'set default'})
    cybersource_merchant_id = fields.Char(required_if_provider='cybersource', string="Merchant id")
    cybersource_key = fields.Char(required_if_provider='cybersource', string="Key")

    def _get_default_payment_method_id(self, code):
        self.ensure_one()
        if self.code != 'cybersource':
            return super(Paymentprovider, self)._get_default_payment_method_id(code)
        return self.env.ref('aspl_payment_cybersource.payment_method_cyberSource').id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: