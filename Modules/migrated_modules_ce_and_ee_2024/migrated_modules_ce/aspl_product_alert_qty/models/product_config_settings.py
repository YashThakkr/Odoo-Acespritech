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
import ast

from odoo import api, fields, models, _

class ProductAlertConfigSettingsWizard(models.TransientModel):
    _inherit = 'res.config.settings'

    alert_user_ids = fields.Many2many('res.users', string="Alert Users")
    alert_email_id = fields.Many2one('mail.template', string="Select Email Template")

    @api.model
    def get_values(self):
        res = super(ProductAlertConfigSettingsWizard, self).get_values()
        config_param_obj = self.env['ir.config_parameter']

        # Retrieve alert_user_ids parameter
        alert_user_ids = config_param_obj.sudo().get_param('alert_user_ids')
        if alert_user_ids:
            # Parse the string representation of the Many2many field into a list of tuples
            alert_user_ids = [(6, 0, ast.literal_eval(alert_user_ids))]  # Assuming the stored value is a list of user IDs
            res.update({'alert_user_ids': alert_user_ids})

        # Retrieve alert_email_id parameter
        alert_email_id = config_param_obj.sudo().get_param('alert_email_id')
        if alert_email_id:
            res.update({'alert_email_id': int(alert_email_id) if alert_email_id else False})
        return res

    def set_values(self):
        super(ProductAlertConfigSettingsWizard, self).set_values()
        config_param_obj = self.env['ir.config_parameter'].sudo()

        # Set alert_user_ids parameter
        if self.alert_user_ids:
            # Convert the Many2many field into a list of user IDs
            alert_user_ids = self.alert_user_ids.ids
            config_param_obj.set_param("alert_user_ids", alert_user_ids)
        else:
            config_param_obj.set_param("alert_user_ids", False)

        # Set alert_email_id parameter
        if self.alert_email_id:
            config_param_obj.set_param("alert_email_id", self.alert_email_id.id)
        else:
            config_param_obj.set_param("alert_email_id", False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
