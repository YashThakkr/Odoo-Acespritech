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
from odoo import api, models


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['hobex_sofort'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        res['hobex_paypal'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        res['hobex_credit_card'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
