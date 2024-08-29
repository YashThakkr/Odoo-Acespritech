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

from odoo import fields, models, _
from odoo.http import request


class Paymentprovider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('hobex_credit_card', 'Hobex Credit Card'), ('hobex_paypal', 'Hobex Paypal'),
                       ('hobex_sofort', 'Hobex Sofort')],
        ondelete={'hobex_credit_card': 'set default', 'hobex_paypal': 'set default', 'hobex_sofort': 'set default'})

    hobex_userId = fields.Char(string="User ID")
    hobex_password = fields.Char(string="Password")
    hobex_entityId = fields.Char(string="Entity ID")
    hobex_url = fields.Char(string="URL")
    hobex_accesstoken = fields.Char(string="Access Token")

    def _get_default_payment_method_id(self,code):
        self.ensure_one()
        if self.code == 'hobex_credit_card':
            return self.env.ref('aspl_payment_hobex.payment_method_hobex_credit_card').id
        elif self.code == 'hobex_paypal':
            return self.env.ref('aspl_payment_hobex.payment_method_hobex_paypal').id
        elif self.code == 'hobex_sofort':
            return self.env.ref('aspl_payment_hobex.payment_method_hobex_sofort').id
        else:
            return super(Paymentprovider, self)._get_default_payment_method_id(code)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
