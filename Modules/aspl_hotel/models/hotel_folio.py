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
from datetime import date, datetime
from odoo.exceptions import UserError


class HotelFolio(models.Model):
    _name = "hotel.folio"
    _rec_name = "number"
    _description = "hotel folio"

    @api.depends('service_ids', 'activity_ids', 'folio_services', 'room_line_ids', 'hotel_room_transfer_ids')
    def _total_amount(self):
        total = 0
        for folio in self:
            for each_service in folio.service_ids:
                total += each_service.amount
            for each_activity in folio.activity_ids:
                total += each_activity.charges
            for each_folio_service in folio.folio_services:
                total += each_folio_service.amount
            for each_room_line in folio.room_line_ids:
                each_room_line.sub_total = each_room_line.price * folio.days
                total += each_room_line.price * folio.days
            for each_room_transfer in folio.hotel_room_transfer_ids:
                total += each_room_transfer.sub_total
            for each_transport in folio.pickup_drop_ids:
                if each_transport.is_include_in_hotel and not each_transport.is_external_agency:
                    total += each_transport.transportation_charges
            folio.total_amount = total

    number = fields.Char(index=True, required=True, copy=False, readonly=True,
                         default=lambda self: _('New'))
    checkin_date = fields.Datetime(string="Check In", required=True)
    checkout_date = fields.Datetime(string="Check Out", required=True)
    days = fields.Float(string="No of Days", compute="_compute_number_of_days")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    room_category = fields.Selection([('room', 'Room'),('conference_room', 'Conference Room'),
                                    ('banquet', 'Banquet')], string="Category")
    folio_services = fields.One2many('hotel.folio.services', 'folio_id', string="Folio Services")
    room_ids = fields.Many2many('hotel.room', string="Rooms")
    state = fields.Selection([('active', 'Active'),
                              ('done', 'Done'),
                              ('closed', 'Closed'),
                              ('invoiced', 'Invoiced')], string="state", default="active")
    activity_ids = fields.One2many('hotel.customer.activity', 'folio_id', string="Activities")
    service_ids = fields.One2many('hotel.laundry.service.line', 'folio_id', string="Services")
    pickup_drop_ids = fields.One2many('hotel.pickup.drop', 'folio_id', string="Pickup & Drop")
    walk_in_id = fields.Many2one('walk.in.detail', 'Walk In Reference')
    room_line_ids = fields.One2many('hotel.room.line', 'folio_id', string="Room Lines")
    total_amount = fields.Monetary(string="Total Amount", readonly=True,
        compute='_total_amount', tracking=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    invoice_count = fields.Integer('Invoice count', compute='compute_invoice_ids')
    hotel_room_transfer_ids = fields.One2many('hotel.room.transfer', 'folio_id',
        string="Hotel Room Transfer")
    discount_type = fields.Selection([('fixed_amount', 'Fixed Amount'),
                                      ('percentage_discount', 'Percentage')],
                                     string="Discount Type")
    discount_rate = fields.Float(string="Discount Rate")
    discount = fields.Monetary(string="Discount", compute='_compute_net_total')
    net_total = fields.Monetary(string="Net Total", compute='_compute_net_total')
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    @api.onchange('pickup_drop_ids')
    def onchange_pickup_drop_ids(self):
        for pickUp in self.pickup_drop_ids:
            pickUp.booking_reference_id = self.walk_in_id.id

    @api.depends('discount_rate', 'total_amount', 'discount_type')
    def _compute_net_total(self):
        if self.discount_type == 'fixed_amount':
            if self.discount_rate <= self.total_amount:
                self.discount = self.discount_rate
            else:
                raise UserError(_("Discount Cannot be more than Total"))
        if self.discount_type == 'percentage_discount':
            if self.discount_rate <= 100:
                self.discount = (self.total_amount * self.discount_rate) / 100
            else:
                raise UserError(_("Discount rate cannot be more than 100%"))
        self.net_total = (self.total_amount - self.discount)

    def compute_invoice_ids(self):
        account_invoice = self.env['account.move'].search([('folio_id', '=', self.id)])
        self.invoice_count = len(account_invoice)

    def open_invoices(self):
        account_invoice_id = self.env['account.move'].search(
            [('folio_id', '=', self.id)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('is_folio_invoice', '=', True), ('id', 'in',
            [each_invoice.id for each_invoice in account_invoice_id])]
        for invoice in account_invoice_id:
            invoice.discount_type = self.discount_type
            invoice.discount_rate = self.discount_rate
            invoice.discount = self.discount
            invoice.net_total = self.net_total
        return action

    @api.constrains('checkin_date', 'checkout_date')
    def validate_date(self):
        if self.checkin_date > self.checkout_date:
            raise UserError(_("Check Out Date Must Be Greater Than Check In Date"))

    @api.depends('checkin_date', 'checkout_date')
    def _compute_number_of_days(self):
        for folio in self:
            folio.days = 0
            if folio.checkin_date and folio.checkout_date:
                difference = datetime.strptime(str(folio.checkout_date), '%Y-%m-%d %H:%M:%S') - datetime.strptime(
                    str(folio.checkin_date), '%Y-%m-%d %H:%M:%S')
                folio.days = (1.0 if difference.days == 0 else difference.days)

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('hotel.folio')
        return super(HotelFolio, self).create(vals)

    def action_close(self):
        self.write({'state': 'closed'})

    def action_done(self):
        self.write({'state': 'done'})
        self.walk_in_id.state = 'check_out'
        self.room_ids.status = 'available'

    def action_create_hotel_invoice(self):
        print("\n\n\n action_create_hotel_invoice________")
        amount_paid = sum(self.env['account.move'].search([('folio_id', '=', self.id)]).mapped('amount_total'))
        amount = self.total_amount - amount_paid
        account_id = self.env['account.account'].search([('code', '=', 400000)])
        invoice_id = self.env['account.move'].create({'partner_id': self.customer_id.id,
                                                      'is_folio_invoice': True,
                                                      'folio_id': self.id,
                                                      'move_type': 'out_invoice',
                                                      'invoice_date': str(datetime.today()),
                                                      'invoice_line_ids': [(0, 0, {
                                                            'display_type': 'product',
                                                            'name': self.number,
                                                            'account_id': account_id.id if account_id else self.customer_id.property_account_payable_id.id,
                                                            'price_unit': amount,
                                                            'quantity': 1
                                                        })],
        })
        print("\n\n\n invoice_id action_create_hotel_invoice-------",invoice_id, "\n\n", invoice_id.invoice_line_ids)
        for pickUp in self.pickup_drop_ids:
            if pickUp.is_include_in_hotel and pickUp.is_external_agency:
                invoice_id = self.env['account.move'].create({
                    'partner_id': self.customer_id.id,
                    'is_folio_invoice': True,
                    'folio_id': self.id,
                    'move_type': 'out_invoice',
                    'invoice_date': str(datetime.today()),
                    'invoice_line_ids': [(0, 0, {
                            'display_type': 'product',
                            'name': self.number,
                            'account_id': account_id.id if account_id else self.customer_id.property_account_payable_id.id,
                            'price_unit': pickUp.transportation_charges,
                            'quantity': 1
                        })],
                })
        if invoice_id:
            self.state = 'invoiced'


class move_line(models.Model):
    _inherit = 'account.move.line'

    @api.model_create_multi
    def create(self, vals):
        res = super(move_line, self).create(vals)
        print("\n\n\n res",res)
        return res


class HotelFolioServices(models.Model):

    _name = "hotel.folio.services"
    _description = "hotel folio services"

    folio_id = fields.Many2one('hotel.folio', string="Folio")
    service_id = fields.Many2one('product.product', string="Service")
    amount = fields.Float(string="Amount")

    @api.onchange('service_id')
    def onchange_service(self):
        if self.service_id:
            self.amount = self.service_id.lst_price


class HotelCustomerActivity(models.Model):
    _name = "hotel.customer.activity"
    _description = "hotel customer activity"

    customer_id = fields.Many2one('res.partner', string="Customer")
    folio_id = fields.Many2one('hotel.folio', string="Folio")
    date = fields.Date(string="Date")
    activity_id = fields.Many2one('hotel.room.amenities', string="Activity")
    duration = fields.Float(string="Duration (Hours)")
    charges = fields.Float(string="Charges")
    state = fields.Selection([('draft', 'Draft'),
                              ('paid', 'Paid')], string="State", default="draft")
    note = fields.Text(string="Note")


class HotelRoomLine(models.Model):
    _name = "hotel.room.line"
    _description = "Hotel Room Line"

    folio_id = fields.Many2one('hotel.folio', string="Folio")
    room_id = fields.Many2one('hotel.room', string="Room No", copy=False)
    checkin_date = fields.Datetime(string='Check In', required=True)
    checkout_date = fields.Datetime(string="Check Out", required=True)
    walk_in_id = fields.Many2one('walk.in.detail', string="Walk In", copy=False, required=True)
    discount = fields.Float(string="Discount(%)")
    price = fields.Float(string="Price")
    description = fields.Char(string="Description", related='walk_in_id.number')
    sub_total = fields.Float(string="Sub Total")


class HotelRoomTransfer(models.Model):
    _name = "hotel.room.transfer"
    _description = "Hotel Room Transfer"

    folio_id = fields.Many2one('hotel.folio', string="Folio")
    from_room_id = fields.Many2one('hotel.room', string="From Room No", copy=False, required=True)
    to_room_id = fields.Many2one('hotel.room', string="To Room No", copy=False, required=True)
    transfer_date = fields.Datetime(string='Room Transfer', required=True)
    walk_in_id = fields.Many2one('walk.in.detail', string="Walk In", copy=False, required=True)
    price = fields.Float(string="Price")
    reason = fields.Char(string="Reason")
    sub_total = fields.Float(string="Sub Total")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
