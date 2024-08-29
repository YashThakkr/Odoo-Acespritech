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
from odoo.exceptions import UserError


class HotelCancellationPolicy(models.Model):
    _name = "hotel.cancellation.policy"
    _rec_name = "start_date"
    _description = "Hotel Cancellation Policy"

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    room_category = fields.Selection([('room', 'Room'),
                        ('banquet', 'Banquet'),('conference', 'Conference')],
                        string="Category", required=True)
    room_cancellation_ids = fields.One2many('hotel.cancellation.policy.line', 'cancellation_id',
                                            string='Room Cancellation')
    cancellation_ids = fields.One2many('hotel.cancellation.policy.line', 'cancellation_id',
        string='Cancellation')
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    @api.constrains('start_date', 'end_date')
    def validate_date(self):
        if self.start_date > self.end_date:
            raise UserError(_("End Date Must Be Greater Than Start Date"))


class HotelCancellationPolicyLine(models.Model):
    _name = "hotel.cancellation.policy.line"
    _description = "Hotel Cancellation Policy Line"

    days_before = fields.Integer(string="Days Before")
    percentage_of_deduction = fields.Float(string="Percentage Of Deduction", required=True)
    room_type_id = fields.Many2one('hotel.room.type', string="Room Type")
    cancellation_id = fields.Many2one('hotel.cancellation.policy', string="Cancellation ID", invisible=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
