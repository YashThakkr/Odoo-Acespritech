# -*- coding: utf-8 -*-
##############################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
##############################################################################
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    time_count = fields.Integer(string="Time Limit")

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            time_count=self.env['ir.config_parameter'].sudo().get_param('aspl_systray_package.time_count')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('aspl_systray_package.time_count', self.time_count)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
