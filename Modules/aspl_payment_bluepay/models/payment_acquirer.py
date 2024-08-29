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

from odoo import fields, models


class AcquirerMasterCard(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('bluepay', 'bluepay')], ondelete={'bluepay': 'set default'})
    account_id = fields.Char(string='Account ID', required_if_provider='bluepay', groups='base.group_user')
    merchant_name = fields.Char(string='Account Name', required_if_provider='bluepay', groups='base.group_user')
    bluepay_secret_key = fields.Char(string='Secret Key', required_if_provider='bluepay', groups='base.group_user')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
