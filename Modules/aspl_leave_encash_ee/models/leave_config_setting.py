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


class LeaveConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    encash_leave = fields.Float(string="Encash Leave")

    def get_values(self):
       res = super(LeaveConfigSetting, self).get_values()
       res.update({'encash_leave':
                                float(self.env['ir.config_parameter'].sudo().get_param('encash_leave')) or False})
       return res

    def set_values(self):
       res = super(LeaveConfigSetting, self).set_values()
       self.env['ir.config_parameter'].sudo().set_param('encash_leave',
                                                            self.encash_leave or '')
       return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
