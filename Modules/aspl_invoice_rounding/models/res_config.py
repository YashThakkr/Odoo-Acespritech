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

from odoo import models, fields, _


class ResConfigSetting(models.TransientModel):
    _inherit = "res.config.settings"

    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            enable_invoice_amount_rounding=bool(params.get_param('enable_invoice_amount_rounding')),
            rounding_option=params.get_param('rounding_option')
        )
        return res

    def set_values(self):
        res = super(ResConfigSetting, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('enable_invoice_amount_rounding', self.enable_invoice_amount_rounding)
        params.set_param('rounding_option', self.rounding_option)

    enable_invoice_amount_rounding = fields.Boolean('Enable Invoice Rounding')
    rounding_option = fields.Selection([('digits', 'Digits'), ('points', 'Points')], default='digits', string="Rounding Options")
    rounding_account_id = fields.Many2one('account.account', string="Rounding Account", config_parameter='aspl_invoice_rounding.rounding_account_id')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
