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
from datetime import datetime, date, timedelta


class PickupDrop(models.Model):
    _name = "hotel.pickup.drop"
    _rec_name = "service_no"
    _description = "Pickup and drop"

    service_no = fields.Char(index=True, copy=False, readonly=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer Name')
    mobile = fields.Char(related='customer_id.mobile')
    email = fields.Char(related='customer_id.email', readonly=False)
    street = fields.Char(related='customer_id.street', readonly=False)
    street2 = fields.Char(related='customer_id.street2', readonly=False)
    zip = fields.Char(related='customer_id.zip', readonly=False, change_default=True)
    city = fields.Char(related='customer_id.city', readonly=False)
    state_id = fields.Many2one("res.country.state", string='State ',
        ondelete='restrict', domain="[('country_id', '=?', country_id)]",
        related='customer_id.state_id', readonly=False)
    country_id = fields.Many2one('res.country', string='Country',
        ondelete='restrict', related='customer_id.country_id', readonly=False)
    booking_reference_id = fields.Many2one('walk.in.detail', string='Booking Reference', required=True)
    folio_id = fields.Many2one('hotel.folio', string='Related Folio')
    transportation_type = fields.Selection([('pick', "Pickup"), ('drop', "Drop"),('both', "Both")],
    	string='Transportation Type', default='pick')
    is_external_agency = fields.Boolean('Is External Agency')
    agency_partner_id = fields.Many2one('res.partner', string='Transportation Partner')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    driver_id = fields.Many2one('res.partner', string='Driver Name', related='vehicle_id.driver_id')
    driver_mobile = fields.Char(related='driver_id.mobile', string='Mobile ')
    transportation_charges = fields.Float('Charge')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    is_include_in_hotel = fields.Boolean('Is Include In Hotel')
    service_type = fields.Selection([('free', "Free"), ('paid', "Paid")],
        string='Service Type', default='free')
    invoice_count = fields.Integer('Invoice count', compute='compute_invoice_ids')
    state = fields.Selection([('draft', 'Draft'), ('pick_up', 'Picked'), ('drop', 'Droped'),
                              ('invoiced', 'Invoiced'), ('done', 'Done')], string="State",
                              default="draft")
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())

    def compute_invoice_ids(self):
        account_invoice_id = self.env['account.move'].search([
            ('walk_in_id', '=', self.booking_reference_id.id),('pickup_drop_invoice','=', True)])
        self.invoice_count = len(account_invoice_id)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['service_no'] = self.env['ir.sequence'].next_by_code('hotel.pickup.drop')
        return super(PickupDrop, self).create(vals)

    def open_invoices(self):
        account_invoice_id = self.env['account.move'].search(
            [('walk_in_id', '=', self.booking_reference_id.id),('pickup_drop_invoice','=', True)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('pickup_drop_invoice', '=', True), ('id', 'in',
            [each_invoice.id for each_invoice in account_invoice_id])]
        return action

    def action_pick_up(self):
        self.state = 'done' if self.service_type == 'free' else 'pick_up'

    def action_drop(self):
        self.state = 'done' if self.service_type == 'free' else 'drop'

    def action_create_invoice(self):
        account_id = self.env['account.account'].search([('code', '=', 400000)])
        if self.is_external_agency:
            customer_id = self.env.user.partner_id.id
        else :
            customer_id = self.customer_id.id
        invoice_id = self.env['account.move'].create({'partner_id': customer_id,
                                                      'move_type': 'out_invoice',
                                                      'is_folio_invoice': True,
                                                      'pickup_drop_invoice' : True,
                                                      'folio_id': self.folio_id.id,
                                                      'walk_in_id': self.booking_reference_id.id,
                                                      'invoice_date': str(datetime.today()),
                                                      'invoice_line_ids': [(0, 0, {
                                                            'display_type': 'product',
                                                            'name': self.service_no,
                                                            'account_id': account_id.id if account_id else self.customer_id.property_account_payable_id.id,
                                                            'price_unit': self.transportation_charges,
                                                            'quantity': 1
                                                        })],
        })
        if invoice_id:
            self.write({'invoice_id': invoice_id,
                        'state': 'invoiced'})

    @api.onchange('booking_reference_id')
    def onchnage_booking_ref(self):
        partner_id = self.env['res.partner'].search([
            ('email','ilike', self.booking_reference_id.email)], limit=1)
        if self.folio_id:
            self.customer_id = self.folio_id.customer_id.id
        else :
            self.customer_id = partner_id
