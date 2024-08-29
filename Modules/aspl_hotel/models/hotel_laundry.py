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


class HotelLaundryServiceType(models.Model):
    _name = "hotel.laundry.service.type"
    _description = "Hotel Laundry Service Type"

    name = fields.Char(string="Service Type", required=True)
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelLaundryItem(models.Model):
    _name = "hotel.laundry.item"
    _description = "Hotel Laundry Item"

    name = fields.Char(string="Name", required=True)
    service_for = fields.Selection([('men', 'Men'),
                                    ('women', 'Women')], string="Service For")
    item_service_ids = fields.One2many('hotel.laundry.item.service', 'item_id', string="Services")
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelLaundryItemService(models.Model):
    _name = "hotel.laundry.item.service"
    _rec_name = "service_type_id"
    _description = "Hotel Laundry Item Service"

    item_id = fields.Many2one('hotel.laundry.item', string="Item")
    service_type_id = fields.Many2one('hotel.laundry.service.type', string="Type")
    amount = fields.Float(string="Amount")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelLaundryService(models.Model):
    _name = "hotel.laundry.service"
    _rec_name = "service_no"
    _description = "HotelLaundryService"

    folio_id = fields.Many2one('hotel.folio', string="Folio", required=True,
        domain="[('room_ids', 'in', room_id), ('state', '=', 'active')]")
    room_id = fields.Many2one('hotel.room', string="Room", required=True,
        domain="[('status', '=', 'occupied')]")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    service_no = fields.Char(index=True, copy=False, readonly=True,
        default=lambda self: _('New'))
    no_of_cloth = fields.Integer(string="No of Clothes", required=True)
    laundry_agancy_id = fields.Many2one("res.partner", string="Agency")
    state = fields.Selection([('draft', 'Draft'),
                              ('collected', 'Collected'),
                              ('assigned', 'Assigned'),
                              ('received', 'Received'),
                              ('delivered', 'Delivered')], string="state", default="draft")
    untax_amount = fields.Float(string="Untaxed Amount", compute='_amount_all')
    tax_amount = fields.Float(string="Taxes")
    total_amount = fields.Float(string="Total")
    service_ids = fields.One2many('hotel.laundry.service.line', 'service_id', string="Services")
    agency_assign_ids = fields.One2many('laundry.assign.agency', 'assign_id', string="Agencys")
    hotel_receive_cloth_ids = fields.One2many('laundry.hotel.receive.cloth', 'assign_id',
        string="Received Cloth")
    count_laundry_cloth = fields.Integer('Laundry Received Cloth Count')
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['service_no'] = self.env['ir.sequence'].next_by_code('hotel.laundry.service')
        return super(HotelLaundryService, self).create(vals)

    @api.onchange('service_ids')
    def onchange_service(self):
        quantity = 0
        for line in self.service_ids:
            quantity += line.quantity
            laundry_item_ids = self.env['hotel.laundry.item'].search([('id', '=', line.item_id.id)])
            if laundry_item_ids:
                if self.no_of_cloth >= quantity:
                    amount = 0
                    for type_id in laundry_item_ids.item_service_ids:
                        for line_type in line.item_service_ids:
                            if line_type._origin.id == type_id.id:
                                amount += type_id.amount
                            line.amount = amount * line.quantity
                            if line:
                                self._amount_all()
                else:
                    raise UserError(_("Quantity is Greater than No Of Cloths"))

    def _amount_all(self):
        amount_untaxed = 0.0
        for service_line in self.service_ids:
            amount_untaxed += service_line.amount
        self.untax_amount = amount_untaxed
        self.total_amount = amount_untaxed

    @api.onchange('room_id')
    def onchange_room(self):
        folio_id = self.env['hotel.folio'].search([('room_ids', 'in', self.room_id.id), ('state', '=', 'active')],
                                                  order="id desc", limit=1)
        if folio_id:
            self.folio_id = folio_id.id
        else:
            self.folio_id = False

    def action_collect(self):
        quantity = 0
        for line in self.service_ids:
            quantity += line.quantity
        if quantity < self.no_of_cloth:
            raise UserError(_("Quantity is Less than No Of Cloths"))
        self.write({'state': 'collected'})
        for line in self.service_ids:
            line.folio_id = self.folio_id.id
            laundry_vals = {'item_id': line.item_id.id,
                            'item_quantity': line.quantity,
                            'receive_quantity': 0,
                            'assign_id': self.id,
                            'state': 'pending'}
            self.write({'hotel_receive_cloth_ids': [(0, 0, laundry_vals)]})

    def action_receive(self):
        receive_cloth = []
        for line in self.hotel_receive_cloth_ids:
            if line.state == 'pending':
                if line.receive_quantity:
                    quantity = line.item_quantity - line.receive_quantity
                    receive_cloth.append([0, 0, {'item_name': line.item_id.name,
                                                 'item_id': line.item_id.id,
                                                 'hotel_laundry_line_id': line.id,
                                                 'deliver_quantity': quantity}])
                else:
                    receive_cloth.append([0, 0, {'item_name': line.item_id.name,
                                                 'item_id': line.item_id.id,
                                                 'hotel_laundry_line_id': line.id,
                                                 'deliver_quantity': line.item_quantity}])

        receive_cloths = self.env['wizard.hotel.receive.cloths'].create({
            'receive_cloth_ids': receive_cloth})

        return {
            'res_id': receive_cloths.id,
            'name': "Hotel Received Laundry Cloth Form",
            'res_model': 'wizard.hotel.receive.cloths',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('aspl_hotel.view_wizard_hotel_receive_cloths_tree_view').id,
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    def action_assign(self):
        self.write({'state': 'assigned'})
        for line in self.service_ids:
            laundry_vals = {'item_id': line.item_id.id,
                            'quantity': line.quantity,
                            'assign_id': self.id,
                            'state': 'assign'}
            self.write({'agency_assign_ids': [(0, 0, laundry_vals)]})

    def action_agency_receive_cloths(self):
        for agency in self.agency_assign_ids:
            agency.state = 'received'
            self.count_laundry_cloth += agency.quantity

    def action_deliver(self):
        self.write({'state': 'delivered'})
        for each_receive_cloth_line in self.hotel_receive_cloth_ids:
            each_receive_cloth_line.state = 'delivered'
        for each in self.agency_assign_ids:
            each.state = 'delivered'


class HotelLaundryServiceLine(models.Model):
    _name = "hotel.laundry.service.line"
    _description = "Hotel Laundry Service Line"

    folio_id = fields.Many2one('hotel.folio', string="Folio")
    room_id = fields.Many2one('hotel.room', string="Room", required=True,
        domain="[('status', '=', 'occupied')]")
    service_id = fields.Many2one('hotel.laundry.service', string="Service", invisible="1")
    item_id = fields.Many2one('hotel.laundry.item', string="Cloth")
    item_service_ids = fields.Many2many('hotel.laundry.item.service', string="Item Service")
    quantity = fields.Integer(string="Quantity")
    amount = fields.Float(string="Amount")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    @api.model
    def create(self, vals):
        service = self.env['hotel.laundry.service'].browse(vals.get('service_id'))
        vals['room_id'] = service.room_id.id
        return super(HotelLaundryServiceLine, self).create(vals)


class LaundryAgencyAssign(models.Model):
    _name = "laundry.assign.agency"
    _description = "Laundry Agency Assign"

    assign_id = fields.Many2one('hotel.laundry.service', string="Assign")
    item_id = fields.Many2one('hotel.laundry.item', string="Cloth")
    quantity = fields.Integer(string="Quantity")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    state = fields.Selection([('assign', 'Assign'),
                              ('pending', 'Pending'),
                              ('received', 'Received'),
                              ('delivered', 'Delivered')], string="State")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class LaundryHotelReceiveCloth(models.Model):
    _name = "laundry.hotel.receive.cloth"
    _description = "Laundry Hotel Receive Cloth"

    assign_id = fields.Many2one('hotel.laundry.service', string="Assign")
    item_id = fields.Many2one('hotel.laundry.item', string="Cloth")
    receive_quantity = fields.Integer(string="Receive Quantity")
    item_quantity = fields.Integer(string="Item Quantity")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    state = fields.Selection([('pending', 'Pending'),
                              ('received', 'Received'),
                              ('delivered', 'Delivered')], string="State")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class WizardHotelReceiveCloths(models.Model):
    _name = "wizard.hotel.receive.cloths"
    _description = "Wizard Hotel Receive Cloths"

    receive_cloth_ids = fields.One2many('wizard.hotel.receive.cloths.line', 'receive_cloth_id',
                                        string="Receive Cloths")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    def do_receive(self):
        laundry_id = self.env['hotel.laundry.service'].browse(self._context.get('active_ids', []))
        deliver_cloth_count = 0
        received_cloth_count = 0
        for line in self.receive_cloth_ids:
            if line.deliver_quantity == line.receive_quantity:
                line.hotel_laundry_line_id.write(
                    {'receive_quantity': int(line.hotel_laundry_line_id.receive_quantity) + int(line.receive_quantity),
                     'state': 'received'})
                deliver_cloth_count += line.hotel_laundry_line_id.item_quantity
                received_cloth_count += line.hotel_laundry_line_id.receive_quantity
                laundry_id.state = 'received'
            else:
                line.hotel_laundry_line_id.write(
                    {'receive_quantity': int(line.hotel_laundry_line_id.receive_quantity) + int(line.receive_quantity)})
                deliver_cloth_count += line.hotel_laundry_line_id.item_quantity
                received_cloth_count += line.hotel_laundry_line_id.receive_quantity


class WizardHotelReceiveClothsLine(models.TransientModel):
    _name = "wizard.hotel.receive.cloths.line"
    _description = "Wizard Hotel Receive Cloths Line"

    receive_cloth_id = fields.Many2one('wizard.hotel.receive.cloths', string="cloths")
    hotel_laundry_line_id = fields.Many2one('laundry.hotel.receive.cloth',
        string="Hotel Laundry Line")
    item_id = fields.Many2one('hotel.laundry.item', string="Cloth")
    item_name = fields.Char(string="Items", readonly=True)
    deliver_quantity = fields.Integer(string="Deliver Quantity", readonly=True)
    receive_quantity = fields.Integer(string="Receive Quantity")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    @api.onchange('receive_quantity')
    def onchange_receive_quantity(self):
        if self.deliver_quantity < self.receive_quantity :
            raise UserError('Received Quantity should not be grater than Delivered Quantity')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
