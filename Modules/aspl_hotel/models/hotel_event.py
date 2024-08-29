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


from odoo import fields, models, api


class Event(models.Model):
    _inherit = "event.event"

    is_hotel_event = fields.Boolean(string="Hotel Event", default=True)
    room_type = fields.Selection([('banquet', 'Banquet'),('conference', 'Conference')],
        default="banquet", string="Type", required=True)
    room_id = fields.Many2one('hotel.room', string="Room No", required=True)
    room_floor_id = fields.Many2one('hotel.floor', string="Floor No", copy=False, required=True)
    room_category = fields.Selection([('room', 'Room'),('banquet', 'Banquet'),
        ('conference', 'Conference')], default="room", string="Category", required=True)
    room_type_id = fields.Many2one('hotel.room.type', string="Room Type", copy=False, required=True)
    walk_in_id = fields.Many2one('walk.in.detail', string="Walk In")
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())
    identity = fields.Many2one('visitor.identity', string='Identity')
    identity_no = fields.Char(string="Identity No", )

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = vals_list[0]
        if vals_list.get('is_hotel_event'):
            partner_id = self.env['res.partner'].sudo().browse(int(vals_list.get('organizer_id')))
            walk_in_id = self.env['walk.in.detail'].sudo().create({'name': partner_id.name,
                                                                   'event_id': self.id,
                                                                   'email': partner_id.email,
                                                                   'mobile_no': partner_id.mobile or '123',
                                                                   'reservation_type': 'hold_confirm_booking',
                                                                   'total_room': 1,
                                                                   'room_category': vals_list.get('room_type'),
                                                                   'room_floor_id': vals_list.get('room_floor_id'),
                                                                   'room_type_id': vals_list.get('room_type_id'),
                                                                   'room_ids': [(6,0,[vals_list.get('room_id')])],
                                                                   'arrival_date': vals_list.get('date_begin'),
                                                                   'departure_date': vals_list.get('date_end'),
                                                                   # 'branch_id': vals_list.get('branch_id'),
                                                                   'identity': vals_list.get('identity'),
                                                                   'identity_no': vals_list.get('identity_no')
                                                                   })
            # vals_list['auto_confirm'] = False
            vals_list['walk_in_id'] = walk_in_id.id
        return super(Event, self).create(vals_list)

    # def write(self, vals):
    #     if vals.get('stage_id'):
    #         stage_id = self.env['event.stage'].browse(vals.get('stage_id'))
    #         if stage_id.name == 'Booked':
    #             if self.walk_in_id.state != 'reserve':
    #                 self.walk_in_id.reservation_action()
    #         elif stage_id.name == 'Announced':
    #             if self.walk_in_id.state != 'check_in':
    #                 self.walk_in_id.check_in_action()
    #         elif stage_id.name == 'Ended':
    #             if self.walk_in_id.state != 'check_out':
    #                 self.walk_in_id.create_folio()
    #                 self.walk_in_id.check_out_action()
    #         elif stage_id.name == 'Cancelled':
    #             if self.walk_in_id.state != 'cancel':
    #                 self.walk_in_id.reservation_cancel_action()
    #     return super(Event, self).write(vals)

    @api.onchange('room_floor_id')
    def _onchange_room_category(self):
        floor_ids = []
        for floor in self.room_floor_id.room_ids:
            floor_ids.append(floor.room_type_id.id)
        return {'domain': {'room_type_id': [('id', 'in', floor_ids)]}}

    def button_confirm(self):
        if self.walk_in_id:
            self.walk_in_id.state = 'check_in'
            self.walk_in_id.reservation_type = 'check_in'
        if self.room_id:
            self.room_id.status = 'booked'
        return super(Event, self).button_confirm()

    def button_done(self):
        res = super(Event, self).button_done()
        self.walk_in_id.state = 'check_out'
        self.walk_in_id.reservation_type = 'check_out'
        self.room_id.status = 'available'
        return res

    def button_cancel(self):
        res = super(Event, self).button_cancel()
        self.walk_in_id.state = 'cancel'
        self.walk_in_id.reservation_type = 'cancel'
        self.room_id.status = 'available'
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: