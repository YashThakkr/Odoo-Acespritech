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
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    weekday_ot_rate = fields.Float(string="Weekday OT Rate")
    weekend_ot_rate = fields.Float(string="Weekend OT Rate")
    holiday_ot_rate = fields.Float(string="Holiday OT Rate")
    ot_time_difference_limit = fields.Integer(string="OT Time Difference Limit")
    manually_create_overtime_req = fields.Boolean()
    payslip_date_range = fields.Boolean()

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_id = self.env['ir.config_parameter'].sudo().get_param
        weekday_ot_rate = float(config_id('aspl_hr_overtime.weekday_ot_rate'))
        holiday_ot_rate = float(config_id('aspl_hr_overtime.weekend_ot_rate'))
        weekend_ot_rate = float(config_id('aspl_hr_overtime.holiday_ot_rate'))
        ot_time_difference_limit = int(config_id('aspl_hr_overtime.ot_time_difference_limit'))
        manually_create_overtime_req = config_id('aspl_hr_overtime.manually_create_overtime_req')
        payslip_date_range = config_id('aspl_hr_overtime.payslip_date_range')
        res.update({'weekday_ot_rate': weekday_ot_rate,
                    'weekend_ot_rate': weekend_ot_rate,
                    'holiday_ot_rate': holiday_ot_rate,
                    'ot_time_difference_limit': ot_time_difference_limit,
                    'manually_create_overtime_req': manually_create_overtime_req,
                    'payslip_date_range': payslip_date_range,
                    })
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        config_param_obj = self.env['ir.config_parameter'].sudo().set_param
        config_param_obj("aspl_hr_overtime.weekday_ot_rate", self.weekday_ot_rate)
        config_param_obj("aspl_hr_overtime.weekend_ot_rate", self.weekend_ot_rate)
        config_param_obj("aspl_hr_overtime.holiday_ot_rate", self.holiday_ot_rate)
        config_param_obj("aspl_hr_overtime.ot_time_difference_limit", self.ot_time_difference_limit)
        config_param_obj("aspl_hr_overtime.manually_create_overtime_req", self.manually_create_overtime_req)
        config_param_obj("aspl_hr_overtime.payslip_date_range", self.payslip_date_range)
        user_ids = self.env['res.users'].search([])
        if self.manually_create_overtime_req:
            group_id = self.env.ref('aspl_hr_overtime.group_overtime_manual_overtime')
            for user in user_ids:
                group_id.write({'users': [(4, user.id)]})
        else:
            group_id = self.env.ref('aspl_hr_overtime.group_overtime_manual_overtime', False)
            for user in user_ids:
                group_id.write({'users': [(3, user.id)]})
        return res

    @api.constrains('weekday_ot_rate', 'weekend_ot_rate', 'ot_time_difference_limit', 'holiday_ot_rate')
    def _check_overtime_configuration(self):
        if self.weekday_ot_rate < 0 or self.weekend_ot_rate < 0 or self.ot_time_difference_limit < 0 or self.holiday_ot_rate < 0:
            raise ValidationError(_('Please enter valid value.'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
