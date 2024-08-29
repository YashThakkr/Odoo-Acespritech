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


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    nutrition_management = fields.Boolean("Nutrition Management")
    feedback = fields.Boolean("Feedback")
    welcome_mail_tmp_id = fields.Many2one("mail.template")
    invoice_mail_tmp_id = fields.Many2one("mail.template")
    membership_renewal_days = fields.Integer("Membership Renewal Days")
    expiry_alert_days = fields.Integer("Expiry Alert Days")

    def get_values(self):
        res = super(ResConfig, self).get_values()
        config_param_obj = self.env['ir.config_parameter'].sudo().get_param
        nutrition_management = config_param_obj('aspl_fitness_management_ee.nutrition_management')
        feedback = config_param_obj('aspl_fitness_management_ee.feedback')
        welcome_mail_tmp_id = int(
            config_param_obj('aspl_fitness_management_ee.welcome_mail_tmp_id'))
        invoice_mail_tmp_id = int(
            config_param_obj('aspl_fitness_management_ee.invoice_mail_tmp_id'))
        membership_renewal_days = int(
            config_param_obj('aspl_fitness_management_ee.membership_renewal_days'))
        expiry_alert_days = int(
            config_param_obj('aspl_fitness_management_ee.expiry_alert_days'))
        res.update({'nutrition_management': nutrition_management,
                    'feedback': feedback,
                    'welcome_mail_tmp_id': welcome_mail_tmp_id,
                    'invoice_mail_tmp_id': invoice_mail_tmp_id,
                    'membership_renewal_days': membership_renewal_days,
                    'expiry_alert_days': expiry_alert_days,
                    })

        return res

    def set_values(self):
        res = super(ResConfig, self).set_values()
        config_param_obj = self.env['ir.config_parameter'].sudo()
        config_param_obj.set_param("aspl_fitness_management_ee.nutrition_management",
                                   self.nutrition_management)
        config_param_obj.set_param("aspl_fitness_management_ee.feedback", self.feedback)
        config_param_obj.set_param("aspl_fitness_management_ee.welcome_mail_tmp_id",
                         self.welcome_mail_tmp_id.id if self.welcome_mail_tmp_id else False)
        config_param_obj.set_param("aspl_fitness_management_ee.invoice_mail_tmp_id",
                         self.invoice_mail_tmp_id.id if self.invoice_mail_tmp_id else False)
        config_param_obj.set_param("aspl_fitness_management_ee.membership_renewal_days",
                         self.membership_renewal_days)
        config_param_obj.set_param("aspl_fitness_management_ee.expiry_alert_days",
                         self.expiry_alert_days)

        group_id = self.env['res.groups'].browse(
            self.env.ref('aspl_fitness_management_ee.nutrition_security_group').id)
        if self.nutrition_management:
            group_id.write({'users': [(4, self.env.uid)]})
        else:
            group_id.write({'users': [(3, self.env.uid)]})

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
