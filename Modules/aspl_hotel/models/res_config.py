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
import ast


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_laundry = fields.Boolean(string="Laundry Service", config_parameter="aspl_hotel.enable_laundry")
    enable_house_keeping = fields.Boolean(string="House Keeping Service",
                                          config_parameter="aspl_hotel.enable_house_keeping")
    enable_pickup_and_drop = fields.Boolean(string="Pick up & drop Service",
                                            config_parameter="aspl_hotel.enable_pickup_and_drop")
    is_agent_commission = fields.Boolean(string='Agent Commission', config_parameter="aspl_hotel.is_agent_commission")
    agent_commission = fields.Float(string="Agent Commission (%)", config_parameter="aspl_hotel.agent_commission")
    cancellation_charges_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')],
                                                 string="Cancellation Charges Type",
                                                 config_parameter="aspl_hotel.cancellation_charges_type")
    cancellation_charges = fields.Float(string="Cancellation Charges",
                                        config_parameter="aspl_hotel.cancellation_charges")
    laundry_stock = fields.Boolean(string="Consider stock during laundry",
                                   config_parameter="aspl_hotel.laundry_stock")
    laundry_location_id = fields.Many2one('stock.location', string="Laundry Location",
                                          config_parameter="aspl_hotel.laundry_location_id")
    is_past_booking = fields.Boolean(string="Past Booking", config_parameter="aspl_hotel.is_past_booking")
    account_id = fields.Many2one('account.account', string='Commission Account',
                                 config_parameter="aspl_hotel.account_id")
    discount_account_id = fields.Many2one('account.account', string="Discount Account",
                                          config_parameter="aspl_hotel.discount_account_id")
    past_booking_record = fields.Integer(string="Past Booking Record",
                                         config_parameter="aspl_hotel.past_booking_record")
    advance_payment_percentage = fields.Float(string="Advance Payment Percentage",
                                              config_parameter="aspl_hotel.advance_payment_percentage")
    hotel_checkin_time = fields.Float(string='Hotel Check In Time', config_parameter="aspl_hotel.hotel_checkin_time")
    hotel_checkout_time = fields.Float(string='Hotel Check Out Time', config_parameter="aspl_hotel.hotel_checkout_time")
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        if self.enable_laundry:
            group_id = self.env.ref('aspl_hotel.group_laundry')
            group_id.write({'users': [(4, self.env.user.id)]})
        else:
            group_id = self.env.ref('aspl_hotel.group_laundry', False)
            group_id.write({'users': [(3, self.env.user.id)]})

        if self.enable_house_keeping:
            group_id = self.env.ref('aspl_hotel.group_house_keeping')
            group_id.write({'users': [(4, self.env.user.id)]})
        else:
            group_id = self.env.ref('aspl_hotel.group_house_keeping', False)
            group_id.write({'users': [(3, self.env.user.id)]})

        if self.enable_pickup_and_drop:
            group_id = self.env.ref('aspl_hotel.group_pickup_drop')
            group_id.write({'users': [(4, self.env.user.id)]})
        else:
            group_id = self.env.ref('aspl_hotel.group_pickup_drop', False)
            group_id.write({'users': [(3, self.env.user.id)]})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
