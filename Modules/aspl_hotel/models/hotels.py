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

from odoo import api, fields, Command, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class WalkIn(models.Model):
    _name = "walk.in.detail"
    _description = "Walk In Detail"
    _rec_name = "number"

    @api.constrains('total_childs', 'total_adult', 'arrival_date', 'departure_date',
        'room_ids','total_room')
    def _check_constrains(self):
        if int(self.total_childs) > sum([room.maximum_child for room in self.room_ids]):
            raise ValidationError(_('No. of Childs is greater then Room Capacity '))
        if int(self.total_adult) > sum([room.maximum_adult for room in self.room_ids]):
            raise ValidationError(_('No. of Adults is greater then Room Capacity '))
        if self.arrival_date >= self.departure_date:
            raise ValidationError(_('Check in Date Should be less than the Check Out Date!'))
        if self.total_room != len(self.room_ids.ids):
            if self.total_room == 0 :
                raise ValidationError(_('Please enter total rooms.'))
            else:
                raise ValidationError(_('You have entered {0} total rooms. Please Select {0} rooms!'.format(self.total_room)))

    number = fields.Char(index=True, readonly=True, required=True, copy=False,
        default=lambda self: _('New'))
    title_id = fields.Many2one('res.partner.title', string="Title")
    name = fields.Char(string="Name", required=True)
    street = fields.Char()
    country_id = fields.Many2one('res.country', string="Country")
    state_id = fields.Many2one('res.country.state', string="State")
    city = fields.Char(string="City")
    zip_code = fields.Char(string="Zip")
    email = fields.Char(string="Email")
    phone_no = fields.Char(string="Phone", size=10)
    mobile_no = fields.Char(string="Mobile", size=10)
    fax = fields.Char(string="Fax")
    identity = fields.Many2one('visitor.identity', string='Identity')
    identity_no = fields.Char(string="Identity No",)
    nationality = fields.Char(string="Nationality")
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')],
        default='m', string="Gender")
    vip_status_id = fields.Many2one('vip.status', string="VIP Status")
    total_room = fields.Integer(string="No. of Rooms", required=True)
    room_floor_id = fields.Many2one('hotel.floor', string="Room Floor", copy=False)
    room_id = fields.Many2one('hotel.room', string="Room", copy=False)
    room_capacity = fields.Integer(string='Room Capacity')
    room_type_id = fields.Many2one('hotel.room.type', string="Room Type", copy=False)
    arrival_date = fields.Datetime(string='Arrival Date', required=True, copy=False)
    departure_date = fields.Datetime(string="Departure Date", required=True, copy=False)
    total_night = fields.Integer(string="No. of Night", copy=False)
    total_adult = fields.Integer(string="No. of Adult", copy=False)
    reservation_type = fields.Selection([('confirm', 'Confirm Booking'),
                                         ('hold_confirm_booking', 'Hold Confirm Booking'),
                                         ('hold_unconfirm_booking', 'Hold Unconfirm Booking'),
                                         ('cancel', 'Cancel'),
                                         ('check_in', 'Check IN'),
                                         ('check_out', 'Check OUT')],
                                        string="Reservation Type", required=True,
                                        default='hold_confirm_booking')
    room_category = fields.Selection([('room', 'Room'),
                                      ('banquet', 'Banquet'),
                                      ('conference', 'Conference')], default="room",
                                      string="Category", required=True)
    total_childs = fields.Integer(string="No. of Child", copy=False)
    business_source = fields.Selection([('normal', 'Normal'), ('contact', 'Contact'),
        ('manual', 'Manual')], string="Business Source")
    agent_id = fields.Many2one('res.partner', domain=[('is_agent', '=', True)], string="Agent")
    commission_plan = fields.Selection([('normal', 'Normal'), ('contact', 'Contact'),
        ('manual', 'Manual')], string="Commission Plan")
    discount_id = fields.Many2one('discount.detail', string="Discount")
    discount_rule_id = fields.Many2one('discount.rule', string="Discount Rule")
    payment_id = fields.Many2one('account.journal', string="Payment Type")
    state = fields.Selection(
        [('walk_in', 'Walk In'), ('reserve', 'Reserve'), ('check_in', 'Check In'),
        ('check_out', 'Check Out'), ('cancel', 'Cancel')], string='Status', default="walk_in")
    color = fields.Integer('Color Index', compute="change_color_on_kanban")
    room_transfer_ids = fields.One2many('room.transfer', 'walk_in_id', string="Room Transfer")
    room_ids = fields.Many2many('hotel.room', string="Select Rooms")
    event_id = fields.Many2one('event.event', string="Event")
    folio_ids = fields.Many2many('hotel.folio', string="Invoice")
    folio_count = fields.Integer('Folio count', compute='compute_folio_ids')
    portal_invoice_paid = fields.Boolean('Portal Invoice Paid')
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())

    def compute_folio_ids(self):
        folio_ids = self.env['hotel.folio'].search([('walk_in_id', '=', self.id)])
        self.folio_count = len(folio_ids)
        self.folio_ids = [(6, 0, [folio.id for folio in folio_ids])]

    def open_folio(self):
        folio_ids = self.env['hotel.folio'].search(
            [('walk_in_id', '=', int(self._context.get('default_walk_in_id')))])
        action = self.env.ref('aspl_hotel.action_hotel_folio').read()[0]
        action['domain'] = [('id', 'in', [each_folio.id for each_folio in folio_ids])]
        return action

    @api.onchange('room_ids')
    def _onchange_room_ids(self):
        self.room_capacity = sum([room.capacity for room in self.room_ids])

    @api.onchange('room_floor_id')
    def _onchange_room_floore(self):
        floor_ids = []
        for floor in self.room_floor_id.room_ids:
            floor_ids.append(floor.room_type_id.id)
        return {'domain': {'room_type_id': [('id', 'in', floor_ids)]}}

    @api.model_create_multi
    def create(self, vals_list):
        res = super(WalkIn, self).create(vals_list)
        res.number = self.env['ir.sequence'].next_by_code('walk.in.detail')
        # if res.room_ids:
        #     if any(room.status == 'booked' for room in res.room_ids):
        #         raise UserError(_('already Booked'))
        return res

    def write(self, vals_list):
        res = super(WalkIn, self).write(vals_list)
        work_order_categ_id = self.env['work.order.categ'].search([('is_cleaning', '=', True)], limit=1)
        if vals_list.get('state') == 'check_out':
            for room in self.room_ids:
                house_keeping_id = self.env['work.order.detail'].create({
                    'work_date': datetime.today(),
                    'work_order_line_ids': [(0, 0, {'room_id': room.id,
                                                    'work_order_categ_id': work_order_categ_id.id if work_order_categ_id
                                                    else None,
                                                    'description': 'Cleaning'})],
                    })
        return res

    @api.model
    def get_resource_view_data(self, day, kwargs):
        branch_ids = self.env['company.branch'].get_allowed_branch_data()
        allowed_branch_ids = [each['id'] for each in branch_ids]
        is_past_booking = self.env['ir.config_parameter'].sudo().get_param(
            'aspl_hotel.is_past_booking')
        no_of_month = self.env['ir.config_parameter'].sudo().get_param(
            'aspl_hotel.past_booking_record')
        today = datetime.today()
        now = datetime.now()
        today_end_date = datetime.strftime(today, "%Y-%m-%d 23:59:59")
        today_start_date = datetime.strftime(today, "%Y-%m-%d 00:00:00")
        resource_lst = []
        event_list = []
        color_dict = {}
        break_time = False
        walk_in_ids = None
        hotel_room = self.env['hotel.room'].sudo().search([('branch_id', 'in', allowed_branch_ids)])
        for each_room in hotel_room:
            resource_lst.append({'id': each_room.id,
                                 'building': each_room.floor_id.name + ' Floor',
                                 'capacity': each_room.maximum_adult + each_room.maximum_child,
                                 'title': each_room.room_no,
                                 'description': '<p><b>Type: </b>' + each_room.room_type_id.name + '<br/><b>Category: </b>' + str(
                                     each_room.room_category).capitalize() + ' <p/>',
                                 'floor': each_room.floor_id.id,
                                 'type': each_room.room_type_id.id,
                                 })
        if is_past_booking:
            no_of_month = self.env['ir.config_parameter'].sudo().get_param(
                'aspl_hotel.past_booking_record')
            past_date = datetime.today() + relativedelta(months=-int(no_of_month))
            start_date = datetime.strftime(past_date, "%Y-%m-%d 00:00:00")
            end_date = datetime.strftime(today, "%Y-%m-%d 23:59:59")
            if kwargs:
                walk_in_ids = self.get_walk_in_from_branch(kwargs, allowed_branch_ids, start_date, end_date)
            else:
                walk_in_ids = self.get_walk_in_ids(start_date, end_date)
        else:
            year_start_date = datetime(now.year, 1, 1)
            start_date = datetime.strftime(year_start_date, "%Y-%m-%d 00:00:00")
            end_date = datetime.strftime(today, "%Y-%m-%d 23:59:59")
            if kwargs:
                walk_in_ids = self.get_walk_in_from_branch(kwargs, allowed_branch_ids, start_date, end_date)
            else:
                walk_in_ids = self.get_walk_in_ids(start_date, end_date)

        for each_event in walk_in_ids:
            color = ''
            if each_event.state == 'reserve':
                color = '#006442'
            elif each_event.state == 'check_in':
                color = '#48929B'
            elif each_event.state == 'check_out':
                color = '#cc0000'
            else:
                color = '#89729E'
            for room in each_event.room_ids:
                event_list.append({
                                   'walk_in_id': each_event.id,
                                   'resourceId': room.id,
                                   'start': str(each_event.arrival_date.date()) + 'T' + str(each_event.arrival_date.time()),
                                   'end': str(each_event.departure_date.date()) + 'T' + str(each_event.arrival_date.time()),
                                   'title': "Walk In: " + each_event.number + ",  Customer: " + each_event.name + ",  Room No: " + room.room_no,
                                   'color': color,
                                   'id':  room.id,
                                   'number': each_event.number,
                                   'customer': each_event.name,
                                   'room_no': room.room_no,
                                   'textColor': 'white',
                                   'status': each_event.state,
                                   'editable': False if each_event.state not in ['reserve', 'check_in'] else True
                                   })
        color_dict.update({'Walk In': '#89729E', 'Reserve': '#006442', 'Check In': '#48929B', 'Check Out': '#cc0000'})
        return [resource_lst, event_list, color_dict]

    @api.model
    def get_walk_in_from_branch(self, kwargs, branch_ids, start_date, end_date):
        # if branch_ids and not kwargs:
        #     walk_in_ids = self.env['walk.in.detail'].sudo().search([('branch_id', 'in', branch_ids),
        #                                                             ('state', '!=', 'cancel'),
        #                                                             '|', ('arrival_date', '>=', start_date),
        #                                                             ('arrival_date', '<=', end_date),
        #                                                             ('departure_date', '>=', start_date)
        #                                                             ], order="arrival_date ASC")
        #     return walk_in_ids
        # elif branch_ids and kwargs:
        #     walk_in_ids = self.env['walk.in.detail'].sudo().search([('branch_id', 'in', branch_ids),
        #                                                             tuple(kwargs),
        #                                                             ('state', '!=', 'cancel'),
        #                                                             '|', ('arrival_date', '>=', start_date),
        #                                                             ('arrival_date', '<=', end_date),
        #                                                             ('departure_date', '>=', start_date)
        #                                                             ], order="arrival_date ASC")
        #     return walk_in_ids
        # else:
        walk_in_ids = self.env['walk.in.detail'].sudo().search([tuple(kwargs),
                                                                ('state', '!=', 'cancel'),
                                                                '|', ('arrival_date', '>=', start_date),
                                                                ('arrival_date', '<=', end_date),
                                                                ('departure_date', '>=', start_date)
                                                                ], order="arrival_date ASC")
        return walk_in_ids

    @api.model
    def get_walk_in_ids(self, start_date, end_date):
        walk_in_ids = self.env['walk.in.detail'].sudo().search([('state', '!=', 'cancel'),
                                                                '|', ('arrival_date', '>=', start_date),
                                                                ('arrival_date', '<=', end_date),
                                                                ('departure_date', '>=', start_date),
                                                                ], order="arrival_date ASC")
        return walk_in_ids

    @api.model
    def remove_booking(self, room_id):
        print("\n\n\n room_id", room_id)
        room_line = []
        room_line_id = int(room_id[1])
        walk_in_id = self.browse(int(room_id[0]))
        if walk_in_id.state == 'walk_in' or walk_in_id.state == 'reserve':
            for room_id in walk_in_id.room_ids:
                print("\n\n\n room id",room_id.id)
                room_line.append(room_id.id)
                print("\n\n\n room_line",room_line)
            for room in room_line:
                if room == room_line_id:
                    room_line.remove(room_line_id)
                    print("\n\n\n room_line", room_line, len(room_line))
                    rec = walk_in_id.write({
                        'room_ids': room_line,
                        'total_room': len(room_line),})
                    print("\n\n\n vals-----",rec)


    @api.model
    def update_resource_view_event_resize(self, walk_in_id, start, end):
        if walk_in_id:
            self.search([('id', '=', walk_in_id)]).write({
                'arrival_date': start, 'departure_date': end})

    @api.model
    def update_resource_view_event_drop(self, walk_in_id, from_room_no, room_id, start_datetime, end_datetime, start_date, end_date, reason):
        room_id = self.env['hotel.room'].sudo().browse(room_id)
        from_room_id = self.env['hotel.room'].sudo().search([('room_no', '=', from_room_no)], limit=1)
        walk_in_id = self.browse(int(walk_in_id))
        if walk_in_id.state != 'cancel':
            if walk_in_id.state in ['reserve', 'check_in']:
                if not str(walk_in_id.arrival_date.date()) == start_date:
                    return False
                else:
                    if str(walk_in_id.departure_date.date()) <= str(date.today()):
                        return False
                    else:
                        walk_in_id = self.update_walk_in_data(walk_in_id, from_room_id, room_id, start_datetime, end_datetime)
                        transfer_id = self.env['room.transfer'].create({'walk_in_id': walk_in_id.id,
                                                                        'from_room_id': from_room_id.id,
                                                                        'to_room_id': room_id.id,
                                                                        'transfer_reason': reason,
                                                                        'room_transfer_date': str(
                                                                            datetime.now().replace(microsecond=0))})
                        # update old room status to maintenance
                        from_room_id.write({
                            'status': 'maintenance'
                        })
                        # work order related to old room maintenance
                        work_order_id = self.env['work.order.detail'].create({
                            'work_date': datetime.today(),
                            'work_order_line_ids': [(0, 0, {'room_id': from_room_id.id,
                                                            'description': reason})],
                        })
                        folio_id = self.env['hotel.folio'].sudo().search([('walk_in_id', '=', walk_in_id.id),
                                                                          ('state', '=', 'active')], order='id desc',
                                                                         limit=1)
                        if folio_id:
                            folio_id.room_ids.status = 'available'
                            folio_id.write({'room_ids': Command.link(transfer_id.to_room_id.id),
                                            'hotel_room_transfer_ids': [(0, 0, {'from_room_id': transfer_id.from_room_id.id,
                                                                                'to_room_id': transfer_id.to_room_id.id,
                                                                                'transfer_date': transfer_id.room_transfer_date,
                                                                                'walk_in_id': walk_in_id.id,
                                                                                'price': transfer_id.to_room_id.rate,
                                                                                'sub_total': transfer_id.to_room_id.rate - transfer_id.from_room_id.rate})]})
                            folio_id.room_ids.status = 'occupied'
                        return walk_in_id
            else:
                if not str(walk_in_id.arrival_date.date()) == start_date:
                    return False

                else:
                    if str(walk_in_id.departure_date.date()) <= str(date.today()):
                        return False
                    else:
                        walk_in_id = self.update_walk_in_data(walk_in_id, from_room_id, room_id, start_datetime, end_datetime)
                        return walk_in_id
        else:
            return False

    def update_walk_in_data(self, walk_in_id, from_room, room_id, start_datetime, end_datetime):
        old_room_list = walk_in_id.room_ids.ids
        new_room_ids = [old_room_list.remove(old_room) for old_room in walk_in_id.room_ids.ids if old_room == from_room.id]
        old_room_list.append(room_id.id)
        if walk_in_id.state == 'reserve':
            room_id.write({
                'status': 'booked'
            })
        elif walk_in_id.state == 'check_in':
            room_id.write({
                'status': 'occupied'
            })
        walk_in_id.write({'arrival_date': str(start_datetime),
                          'departure_date': str(end_datetime),
                          'room_floor_id': room_id.floor_id.id,
                          'room_type_id': room_id.room_type_id.id,
                          'room_ids': [(6, 0, old_room_list)],
                          })
        return walk_in_id

    def create_folio(self):
        context = {}
        if self.email:
            partner_id = self.env['res.partner'].sudo().search([('email', 'ilike', self.email)])
            context.update({'default_res_id': self.id})
            if partner_id:
                context.update({
                    'default_partner_id': partner_id[0].id,
                    'default_email': partner_id[0].email,
                    'default_existing_customer': True,
                    'default_customer_type': 'existing',
                })
            else:
                context.update({
                    'default_email': self.email,
                    'default_mobile_no': self.mobile_no,
                    'default_customer_name': self.name,
                    'default_new_customer': True,
                    'default_customer_type': 'new',
                })
        context.update({'amount': self._context.get('amount', False)})
        return {
            'name': "Customer",
            'res_model': 'wizard.customer.check',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': context
        }

    def advance_payment(self):
        if self.room_ids:
            minimum_amount = 0
            advance_payment_percentage = float(
                self.env['ir.config_parameter'].sudo().get_param('aspl_hotel.advance_payment_percentage'))
            room_amount = sum(room.rate for room in self.room_ids)
            if advance_payment_percentage and room_amount:
                minimum_amount = float(room_amount) * float(advance_payment_percentage) / 100
            return {
                'name': "Room Advance Payment",
                'res_model': 'room.advance.payment',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_minimum_amount': minimum_amount, 'default_amount': minimum_amount}
            }
        else:
            raise UserError(_('Please select room.'))

    def reservation_action(self):
        template_id = self.env.ref('aspl_hotel.hotel_room_booking_confirmation')
        self.state = 'reserve'
        self.reservation_type = 'confirm'
        room_detail_ids = self.env['hotel.room'].search([('id', 'in', self.room_ids.ids)])
        for room in room_detail_ids:
            room.write({'status': 'booked'})
        if template_id:
            template_id.sudo().send_mail(self.id)

    def create_room_lines(self, walk_in_id, folio_id):
        for room in walk_in_id.room_ids:
            folio_id.write({
                'room_line_ids': [
                      (0, 0, {'room_id': room.id,
                              'checkin_date': walk_in_id.arrival_date,
                              'checkout_date': walk_in_id.departure_date,
                              'walk_in_id': walk_in_id.id,
                              'price': room.rate})]
                })

    def check_in_action(self):
        self.state = 'check_in'
        self.reservation_type = 'check_in'
        room_detail_ids = self.env['hotel.room'].search([('id', 'in', self.room_ids.ids)])
        if self.reservation_type == 'check_in':
            template_id = self.env.ref('aspl_hotel.hotel_room_booking_confirmation')
            for room in room_detail_ids:
                room.write({'status': 'booked'})
            if template_id:
                template_id.sudo().send_mail(self.id)
        for room in room_detail_ids:
            room.write({'status': 'occupied'})

    def reservation_cancel_action(self):
        print("\n\n\n reservation_cancel_action >>>>>>>>>>")
        template_id = self.env.ref('aspl_hotel.hotel_room_cancellation')
        print("\n\n\n template id",template_id)
        self.state = 'cancel'
        self.reservation_type = 'cancel'
        days = (self.arrival_date.date() - date.today()).days
        room_detail_ids = self.env['hotel.room'].search([('id', 'in', self.room_ids.ids)])
        print("\n\n\n room_detail_ids",room_detail_ids)
        partner_id = self.env['res.partner'].sudo().search([('email', '=', self.email)])
        print("\n\n\n partner_id",partner_id)
        if not partner_id:
            print("\n\n\n if not partner_id --------",)
            partner_id = self.env['res.partner'].sudo().create({'name': self.name,
                                                                'street': self.street if self.street else "",
                                                                'city': self.city if self.city else "",
                                                                'state_id': self.state_id.id if self.state_id else False,
                                                                'zip': self.zip_code if self.zip_code else "",
                                                                'country_id': self.country_id.id if self.country_id else False,
                                                                'phone': self.phone_no if self.phone_no else '',
                                                                'mobile': self.mobile_no if self.mobile_no else '',
                                                                'gender': self.gender if self.gender else '',
                                                                'vip_status_id': self.vip_status_id.id if self.vip_status_id else False,
                                                                'payment_type_id': self.payment_id.id if self.payment_id else False,
                                                                'is_hotel_customer': True
                                                                })
        cancellation_policy = self.env['hotel.cancellation.policy'].search(
            [('start_date', '<=', date.today()), ('end_date', '>=', date.today()),
             ('branch_id', '=', self.branch_id.id)], limit=1)
        folio_id = self.env['hotel.folio'].sudo().create({'customer_id': partner_id.id,
                                                          'checkin_date': self.arrival_date,
                                                          'checkout_date': self.departure_date,
                                                          'room_ids': self.room_ids.ids,
                                                          'walk_in_id': self.id,
                                                          'room_category': self.room_category,
                                                          'branch_id': self.branch_id.id
        })
        print("\n\n\n folio_id", folio_id)
        self.create_room_lines(self, folio_id)
        if cancellation_policy:
            for each_room in self.room_ids:
                cancellation_policy_type = cancellation_policy.room_cancellation_ids.\
                    filtered(lambda l: l.room_type_id.id == each_room.room_type_id.id)
                amount = (each_room.rate * cancellation_policy_type.percentage_of_deduction) / 100
                print("\n\n\n amount", amount)
        #     for policy in cancellation_policy.room_cancellation_ids:
        #         for each_room in self.room_ids:
        #             if each_room.room_type_id.id == policy.room_type_id.id and policy.days_before == days:
                if amount > 0:
                    print("\n\n\n amount > 0", amount > 0)
                    account_id = self.env['account.account'].search([('code', '=', 400000)])
                    invoice_id = self.env['account.move'].sudo().create({'partner_id': partner_id.id,
                                                                         'is_folio_invoice': True,
                                                                         'folio_id': folio_id.id,
                                                                         'move_type': 'out_invoice',
                                                                         'currency_id': folio_id.currency_id.id,
                                                                         'user_id': self.env.user.id,
                                                                         'invoice_date': str(datetime.today()),
                                                                         'discount_type': folio_id.discount_type,
                                                                         'discount_rate': folio_id.discount_rate,
                                                                         'discount': folio_id.discount,
                                                                         'invoice_line_ids': [
                                                                                (0, 0, {'product_id': '',
                                                                                        'name': folio_id.number,
                                                                                        'account_id': account_id.id,
                                                                                        'quantity': 1.0,
                                                                                        'price_unit': amount})
                                                                                ]
                                                                        })
        for room in room_detail_ids:
            room.write({'status': 'available'})
        if template_id:
            template_id.sudo().send_mail(self.id)

    def check_out_action(self):
        if len(self.folio_ids) < 1:
            raise UserError(_('Please create folio before check out.'))
        self.state = 'check_out'
        self.reservation_type = 'check_out'
        room_detail_ids = self.env['hotel.room'].search([('id', 'in', self.room_ids.ids)])
        room_detail_ids.write({'status': 'available'})
        # for room in room_detail_ids:
        #     room.write({'status': 'available'})

    @api.depends('state')
    def change_color_on_kanban(self):
        """    this method is used to change color index
        base on state    ----------------------------------------
        :return: index of color for kanban view    """

        for walk_in in self:
            color = 0
            if walk_in.state == 'walk_in':
                color = 2
            elif walk_in.state == 'reserve':
                color = 10
            elif walk_in.state == 'cancel':
                color = 1
            elif walk_in.state == 'new':
                color = 7
            else:
                color = 5
            walk_in.color = color


class Discount(models.Model):
    _name = "discount.detail"
    _rec_name = "type"
    _description = "Discount Detail"

    type = fields.Char(string="Discount Type")
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())


class DiscountRule(models.Model):
    _name = "discount.rule"
    _rec_name = "discount_rule"
    _description = "Discount Rule"

    discount_id = fields.Many2one('discount.detail', string="Discount")
    discount_rule = fields.Char(string="Discount Rule")
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())


class VipStatus(models.Model):
    _name = "vip.status"
    _description = "VIP Status"

    name = fields.Char(string="VIP Status")
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())


class VisitorIDProof(models.Model):
    _name = 'visitor.identity'
    _description = "Visitor Identity"

    name = fields.Char(string="Identity")
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())


class WizardCustomerCheck(models.TransientModel):
    _name = "wizard.customer.check"
    _description = "Wizard Customer Check"

    customer_type = fields.Selection([('existing', 'Existing Customer'), ('new', 'New Customer')],
                                     string="Customer Type")
    customer_name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner', string="Partner")
    mobile_no = fields.Char('Mobile No.')
    email = fields.Char('Email')

    def do_create(self):
        print("\n\n\n do create------------>>>>>>>>>>")
        walk_in_id = self.env['walk.in.detail'].sudo().browse(int(self._context.get('default_res_id')))
        folio_id = False
        if self.customer_type == 'new' and walk_in_id:
            print("\n\n ifffffffff______")
            walk_in_id.write({'mobile_no': self.mobile_no,
                              'email': self.email,
                              'name': self.customer_name})
            partner_id = self.env['res.partner'].sudo().create({
                'name': self.customer_name,
                'street': walk_in_id.street if walk_in_id.street else "",
                'city': walk_in_id.city if walk_in_id.city else "",
                'state_id': walk_in_id.state_id.id if walk_in_id.state_id else False,
                'zip': walk_in_id.zip_code if walk_in_id.zip_code else "",
                'country_id': walk_in_id.country_id.id if walk_in_id.country_id else False,
                'phone': walk_in_id.phone_no if walk_in_id.phone_no else '',
                'mobile': walk_in_id.mobile_no if walk_in_id.mobile_no else '',
                'gender': walk_in_id.gender if walk_in_id.gender else '',
                'vip_status_id': walk_in_id.vip_status_id.id if walk_in_id.vip_status_id else False,
                'payment_type_id': walk_in_id.payment_id.id if walk_in_id.payment_id else False,
                'is_hotel_customer': True
            })
            print("\n\n partner_id----",partner_id)
            if partner_id:
                for room in walk_in_id.room_ids :
                    folio_id = self.env['hotel.folio'].sudo().create({
                        'customer_id': partner_id.id,
                        'checkin_date': walk_in_id.arrival_date,
                        'checkout_date': walk_in_id.departure_date,
                        'room_ids': [(6,0, [room.id])],
                        'walk_in_id': walk_in_id.id,
                        # 'branch_id': walk_in_id.branch_id.id,
                        'room_category': walk_in_id.room_category,
                        'room_line_ids': [
                            (0, 0, {'room_id': room.id,
                                    'checkin_date': walk_in_id.arrival_date,
                                    'checkout_date': walk_in_id.departure_date,
                                    'walk_in_id': walk_in_id.id,
                                    'price': room.rate})]
                    })
        else:
            print("\n\n ifffffffff______")
            if self._context.get('default_partner_id'):
                for room in walk_in_id.room_ids:
                    folio_id = self.env['hotel.folio'].sudo().create(
                        {'customer_id': int(self._context.get('default_partner_id')),
                         'checkin_date': walk_in_id.arrival_date,
                         'checkout_date': walk_in_id.departure_date,
                         'room_ids': [(6,0, [room.id])],
                         'walk_in_id': walk_in_id.id,
                         # 'branch_id': walk_in_id.branch_id.id,
                         'room_category': walk_in_id.room_category,
                         'room_line_ids': [
                          (0, 0, {'room_id': room.id,
                                  'checkin_date': walk_in_id.arrival_date,
                                  'checkout_date': walk_in_id.departure_date,
                                  'walk_in_id': walk_in_id.id,
                                  'price': room.rate})]
                            })
        print("\n\n\n folio", folio_id, self._context.get('amount', False))
        if folio_id and self._context.get('amount', False):
            print("\n\n\n invoice",folio_id and self._context.get('amount', False))
            invoice_obj = self.env['account.move'].sudo()
            account_id = self.env['account.account'].search([('code', '=', 400000)])
            invoice_id = invoice_obj.create({'partner_id': folio_id.customer_id.id,
                                             'is_folio_invoice': True,
                                             'folio_id': folio_id.id,
                                             'move_type': 'out_invoice',
                                             'currency_id': folio_id.currency_id.id,
                                             'user_id': self.env.user.id,
                                             'invoice_date': str(datetime.today()),
                                             'discount_type': folio_id.discount_type,
                                             'discount_rate': folio_id.discount_rate,
                                             'discount': folio_id.discount,
                                             'net_total': folio_id.net_total,
                                             'invoice_line_ids': [(0, 0, {'product_id': '',
                                                                          'display_type': 'product',
                                                    'name': folio_id.number,
                                                    'account_id': account_id.id if account_id else folio_id.customer_id.property_account_payable_id.id,
                                                    'quantity': 1.0,
                                                    'price_unit': float(self._context.get('amount', 0.0))})
                                                            ]
                                         })
            print("\n\n\n invoice id", invoice_id, invoice_id.invoice_line_ids)
        # walk_in_id.reservation_action()


class HotelFloor(models.Model):
    _name = "hotel.floor"
    _description = "Hotel Floor"

    name = fields.Char(string="Floor Name", required=True)
    room_type_ids = fields.Many2many('hotel.room.type', string="Room Type")
    color = fields.Char(string="Color", help="Choose your color", size=7)
    active = fields.Boolean(string='Active', default=True)
    room_category = fields.Selection([('room', 'Room'),
                                      ('banquet', 'Banquet'),
                                      ('conference', 'Conference')], string="Category")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())
    room_ids = fields.One2many('hotel.room', 'floor_id')


class BillingInformation(models.Model):
    _name = 'billing.information'
    _description = "Billing Information"

    rates = fields.Selection([('normal', 'Normal'), ('contact', 'Contact'), ('manual', 'Manual')],
        string="Rates")
    bill_to = fields.Selection([('company', 'Company'), ('guest', 'Guest'),
        ('grp_owner', 'Group Owner')], string="Bill To")
    tax_exemption = fields.Float(string='Tax')
    payment_mode = fields.Selection([('cash', 'Cash'), ('credit', 'Credit')], string="Payment Mode")
    release_date = fields.Date(string="Release Date")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class RoomTransfer(models.Model):
    _name = "room.transfer"
    _description = "Room Transfer"

    walk_in_id = fields.Many2one('walk.in.detail', string="Walk in")
    from_room_id = fields.Many2one('hotel.room', string="From Room")
    to_room_id = fields.Many2one('hotel.room', string="To Room")
    room_transfer_date = fields.Datetime(string="Room Transfer")
    transfer_reason = fields.Char(string="Reason")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class StayInformation(models.Model):
    _name = "stay.information"
    _description = "Stay Information"

    room = fields.Char(string="Rooms")
    room_floor_id = fields.Many2one('hotel.floor', string="Room Floor")
    arrival_time = fields.Datetime(string='Arrival')
    departure = fields.Datetime(string="Departure")
    night = fields.Integer(string="Night")
    adult = fields.Integer(string="No. of Adult", copy=False)
    reservation_type = fields.Selection([('confirm', 'Confirm Booking'),
                                         ('hold_confirm_booking', 'hold Confirm Booking'),
                                         ('hold_unconfirm_booking', 'Hold Unconfirm Booking')],
                                        string="Reservation Type", required=True)
    total_childs = fields.Integer(string="Childs")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
