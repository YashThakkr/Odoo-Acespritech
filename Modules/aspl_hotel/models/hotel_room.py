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
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class HotelAmenities(models.Model):
    _name = "hotel.amenities"
    _description = "hotel amenities"

    name = fields.Char(string="Name", required=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelRoomAmenitiesType(models.Model):
    _name = "hotel.room.amenities.type"
    _description = "Hotel Room Amenities Type"

    name = fields.Char(string="Type", required=True)
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelRoomAmenities(models.Model):
    _name = "hotel.room.amenities"
    _description = "Hotel Room Amenities"

    name = fields.Char(string="Name", required=True)
    amenities_type_id = fields.Many2one('hotel.room.amenities.type', string="Amenities Type",
        required=True)
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelRoomType(models.Model):
    _name = "hotel.room.type"
    _description = "Hotel Room Type"

    name = fields.Char(string="Room Type")
    desc = fields.Text(string="Description")

    floor_ids = fields.Many2many('hotel.floor', 'floor_id', string="Floor No")
    taxes_ids = fields.Many2many('account.tax', string="Taxes")
    room_image_ids = fields.One2many('room.type.image', 'room_type_id', string="Room Images")
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class RoomTypeImage(models.Model):
    _name = 'room.type.image'
    _description = "room type image"

    room_type_id = fields.Many2one('hotel.room.type', string="Room Type")
    room_image = fields.Binary(string="Image")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelRoomPriceList(models.Model):
    _name = "hotel.room.pricelist"
    _description = "Hotel Room Price List"

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    item_ids = fields.One2many('hotel.room.pricelist.item', 'pricelist_id', string="Room Price")
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelRoomPriceListItem(models.Model):
    _name = "hotel.room.pricelist.item"
    _description = "Hotel Room Price List Item"

    pricelist_id = fields.Many2one('hotel.room.pricelist', string="Room Pricelist")
    room_type = fields.Many2one('hotel.room.type', string="Room Type")
    want_to = fields.Selection([('increase', 'Increase'),
                                ('decrease', 'Decrease')], string="Want To")
    based_on = fields.Selection([('percentage', 'Percentage'),
                                 ('fix', 'Fixed')], string="Based On")
    percentage = fields.Float(string="Percentage")
    fixed = fields.Float(string="Fixed")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelRoom(models.Model):
    _name = "hotel.room"
    _rec_name = "room_no"
    _description = "Hotel Room"

    @api.constrains('room_no')
    def check_order(self):
        for room in self:
            room_ids = self.search([('room_no', '=', room.room_no), ('id', '!=', room.id)])
            if room_ids:
                raise ValidationError("Room Number must be unique")

    # def _get_computed_branch(self):
    #     self.ensure_one()
    #     if self.room_category:
    #         return self.floor_id.branch_id
    #
    # @api.onchange('room_category')
    # def _onchange_room_category(self):
    #     self.branch_id = self._get_computed_branch()

    floor_id = fields.Many2one('hotel.floor', string="Floor No", required=True)
    room_no = fields.Char(string="Room No", required=True, copy=False, default="0")
    room_type_id = fields.Many2one('hotel.room.type', string="Room Type", required=True)
    capacity = fields.Integer(string="Room Capacity", compute="_count_capacity",
        readonly=True, store=True)
    capacity_related = fields.Integer(string="Capacity")
    status = fields.Selection([('available', 'Available'),
                               ('booked', 'Booked'),
                               ('occupied', 'Occupied'),
                               ('maintenance', 'Under Maintenance')], string="Status", default="available")
    room_category = fields.Selection([('room', 'Room'),
                                     ('banquet', 'Banquet'),
                                     ('conference', 'Conference')], string="Category", required=True)
    maximum_adult = fields.Integer(string="Maximum Adult")
    maximum_child = fields.Integer(string="Maximum Child")
    telephone_ext = fields.Char(string="Telephone Ext", help="room telephone number")
    rate = fields.Float(string="Rate")
    taxes_ids = fields.Many2many('account.tax', string="Taxes")
    active = fields.Boolean(string='Active', default=True)
    no_of_bed = fields.Selection([('Single Bed', 'Single Bed'),
                                  ('Double Bed', 'Double Bed'),
                                  ('Two Beds', 'Two Beds'),
                                  ('Three Beds', 'Three Beds'),
                                  ('Four beds', 'Four beds'),
                                  ('Five Beds', 'Five Beds'),
                                  ('Six Beds', 'Six Beds'),
                                  ('Seven Beds', 'Seven Beds'),
                                  ('Eight Beds', 'Eight Beds'),
                                  ('Nine Beds', 'Nine Beds'),
                                  ('Ten Beds', 'Ten Beds')], string="No of Bed")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())
    walk_in_id = fields.Many2one('walk.in.detail', string='Walk In')

    @api.depends('maximum_adult', 'maximum_child')
    def _count_capacity(self):
        for room in self:
            room.capacity = room.maximum_adult + room.maximum_child
            room.capacity_related = room.maximum_adult + room.maximum_child

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        if self._context.get('walk_in') and (self._context.get('arrival_date') and self._context.get('departure_date')):
            arrival_date = datetime.strptime(self._context.get('arrival_date'), DATETIME_FORMAT)
            departure_date = datetime.strptime(self._context.get('departure_date'), DATETIME_FORMAT)
            room_ids = []
            walk_in_ids = self.env['walk.in.detail'].search([('state', 'in', ['reserve', 'check_in'])])
            for rec in walk_in_ids:
                if rec.arrival_date <= arrival_date <= rec.departure_date\
                        or rec.arrival_date <= departure_date <= rec.departure_date:
                    room_ids.extend([room.id for room in rec.room_ids if room.id not in room_ids])
            domain += [('id', 'not in', room_ids)]
        return super(HotelRoom, self)._search(domain, offset=offset, limit=limit, order=order,
                                              access_rights_uid=access_rights_uid)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
