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

from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockConsigneeTransfer(models.Model):
    _name = 'stock.consignee.transfer'
    _description = 'Consignee Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Consignee",
                                 domain=[('is_consignee', '=', True)])
    to_partner_id = fields.Many2one('res.partner', string="To Consignee",
                                    domain=[('is_consignee', '=', True)])
    destination_location_id = fields.Many2one('stock.location', string="Destination Location")
    source_location_id = fields.Many2one('stock.location', string="Source Location")
    is_return = fields.Boolean(string="Is Return")
    is_internal_transfer = fields.Boolean(string="Internal Transfer")
    lines = fields.One2many('stock.consignee.transfer.line', 'consignee_record_id',
                            string="Stock lines")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
    ], default='draft', string="State", tracking=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id)
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type")
    stock_picking_id = fields.Many2one('stock.picking', string="Stock Picking Ref")
    picking_number_ref = fields.Char(related="stock_picking_id.name", store=True,
                                     string="Stock Picking Number")
    date = fields.Datetime(string="Date")

    @api.model
    def default_get(self, field_list):
        if not self._context.get('default_is_return') and not self._context.get(
                'default_is_internal_transfer'):
            if self.env.user.has_group('aspl_consignee_management.group_stock_consignee'):
                raise ValidationError(_('Consignee can not create transfer request directly.'))
        res = super(StockConsigneeTransfer, self).default_get(field_list)
        picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'internal'), (
            'warehouse_id.company_id', '=', self.env.user.company_id.id)], limit=1)
        if not picking_type_id:
            raise ValidationError(
                _("Warehouse has no internal 'Operation Type' configured. Please configure 'internal Operation Type' first."))
        res.update({'picking_type_id': picking_type_id.id})
        if self._context.get('default_is_internal_transfer'):
            res.update({'partner_id': self.env.user.partner_id.id})
        res.update({'date': datetime.today()})
        return res

    @api.model_create_multi
    def create(self, vals):
        for rec in vals:
            if rec.get('is_return'):
                rec['name'] = self.env['ir.sequence'].next_by_code(
                    'aspl_consignee_management.sequence_consignee_return_transfer')
            elif rec.get('is_internal_transfer'):
                rec['name'] = self.env['ir.sequence'].next_by_code(
                    'aspl_consignee_management.sequence_consignee_internal_transfer')
            else:
                rec['name'] = self.env['ir.sequence'].next_by_code(
                    'aspl_consignee_management.sequence_consignee_transfer')
            if rec.get('partner_id') == rec.get('to_partner_id'):
                raise ValidationError(_('Source and Destination consignee can not be same.'))
        return super(StockConsigneeTransfer, self).create(vals)

    @api.onchange('partner_id', 'to_partner_id')
    def change_location_id(self):
        if self.is_internal_transfer:
            if self.partner_id:
                self.source_location_id = self.partner_id.location_id.id
            if self.to_partner_id:
                self.destination_location_id = self.to_partner_id.location_id.id
        else:
            if self.partner_id:
                if not self.is_return:
                    self.destination_location_id = self.partner_id.location_id
                if self.is_return:
                    self.source_location_id = self.partner_id.location_id

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})

    def action_request(self):
        self.ensure_one()
        self.write({'state': 'request'})
        if not self.lines:
            raise ValidationError(_('Please enter product lines first! '))
        if self.env['ir.config_parameter'].sudo().get_param(
                'aspl_consignee_management.is_send_mail_request'):
            if self.is_return:
                stock_manager_group = self.env.ref('stock.group_stock_manager')
                if stock_manager_group and stock_manager_group.users:
                    emails = "%s" % ','.join(
                        map(str, [user.email for user in stock_manager_group.users]))
                    if emails:
                        template_id = self.env.ref(
                            'aspl_consignee_management.consignee_request_template')
                        template_id.with_context(email_to=emails).send_mail(self.id,
                                                                            force_send=True)
            elif self.is_internal_transfer:
                template_id = self.env.ref(
                    'aspl_consignee_management.consignee_consignee_request_internal_template')
                template_id.send_mail(self.id, force_send=True)
            else:
                template_id = self.env.ref(
                    'aspl_consignee_management.user_consignee_request_template')
                template_id.send_mail(self.id, force_send=True)
        return True

    def action_confirm(self):
        self.ensure_one()
        self.write({'state': 'confirm'})
        if self.env['ir.config_parameter'].sudo().get_param(
                'aspl_consignee_management.is_send_mail_confirm'):
            if self.is_return:
                if self.partner_id.id == self.env.user.partner_id.id and self.env.user.has_group(
                        'aspl_consignee_management.group_stock_consignee'):
                    raise ValidationError(
                        _('Consignee can not confirm their own return transfer request...!'))
                template_id = self.env.ref('aspl_consignee_management.consignee_confirm_template')
                template_id.send_mail(self.id, force_send=True)
            elif self.is_internal_transfer:
                template_id = self.env.ref(
                    'aspl_consignee_management.consignee_consignee_confirm_internal_template')
                template_id.send_mail(self.id, force_send=True)
            else:
                stock_manager_group = self.env.ref('stock.group_stock_manager')
                if stock_manager_group and stock_manager_group.users:
                    emails = "%s" % ','.join(
                        map(str, [user.email for user in stock_manager_group.users]))
                    if emails:
                        template_id = self.env.ref(
                            'aspl_consignee_management.user_consignee_confirm_template')
                        template_id.with_context(email_to=emails).send_mail(self.id,
                                                                            force_send=True)
        return True

    def action_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def action_ready_to_transfer(self):
        self.ensure_one()
        if self.lines.filtered(lambda l: l.transfer_qty == 0):
            raise ValidationError(_(' Transferred quantity is greater than zero!'))

        if self.is_return and self.lines.filtered(lambda l: l.transfer_qty > l.requested_qty):
            raise ValidationError(
                _(' Transferred quantity can not be greater than requested quantity!'))

        stock_obj = self.env['stock.picking']
        line_list = []
        for line in self.lines:
            line_list.append((0, 0, {
                'product_id': line.product_id.id,
                'name': self.picking_type_id.id,
                'quantity': line.requested_qty,
                'location_id': self.source_location_id.id if self.source_location_id else
                self.picking_type_id.default_location_src_id.id,
                'location_dest_id': self.destination_location_id.id if self.destination_location_id
                else self.picking_type_id.default_location_dest_id.id,
                'product_uom_qty': line.transfer_qty,
                'product_uom': line.product_id.uom_po_id.id,
                'picking_type_id': self.picking_type_id.id,
            }))
        if line_list:
            stock_vals = stock_obj.default_get(fields_list=[])
            stock_vals.update({
                'origin': self.name,
                'location_id': self.source_location_id.id if self.source_location_id else
                self.picking_type_id.default_location_src_id.id,
                'location_dest_id': self.destination_location_id.id if self.destination_location_id
                else self.picking_type_id.default_location_dest_id.id,
                'picking_type_id': self.picking_type_id.id,
                'show_lots_text': True,
                'move_ids': line_list
            })
            picking_id = stock_obj.create(stock_vals)
            if picking_id:
                self.write({'stock_picking_id': picking_id.id, 'state': 'done'})
        return True

    def open_stock_picking(self):
        if self.stock_picking_id:
            view_id = self.env.ref('stock.view_picking_form').id
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'view_id': view_id,
                'res_id': self.stock_picking_id.id,
            }

    @api.model
    def get_product_expiry_date_scheduler(self):
        if self.env['ir.config_parameter'].sudo().get_param(
                'aspl_consignee_management.is_send_alert_for_product_expired'):
            consignee_locations = dict((partner['id'], partner['location_id'][0])
                                       for partner in self.env['res.partner'].search_read(
                [('is_consignee', '=', True),
                 ('location_id', '!=', False)],
                ['location_id']))
            start_date = datetime.now()
            quant_obj = self.env['stock.quant'].search([])
            get_days = self.env['ir.config_parameter'].sudo().get_param(
                'aspl_consignee_management.days')
            end_date = start_date + timedelta(days=int(get_days))
            lot_ids = self.env['stock.lot'].search(
                [('expiration_date', '>=', start_date.strftime('%Y-%m-%d %H:%M:%S')),
                 ('expiration_date', '<=', end_date.strftime('%Y-%m-%d %H:%M:%S'))])
            for lot in lot_ids:
                quant_obj += lot.quant_ids

            del_list = []
            for con_loc in consignee_locations:
                con_quant = [{'product_id': quant.product_id,
                              'qty': quant.quantity,
                              'lot_id': quant.lot_id,
                              'expire_date': quant.lot_id.expiration_date} for quant in
                             quant_obj.filtered(
                                 lambda q: q.location_id.id == consignee_locations.get(con_loc))]
                if con_quant:
                    consignee_locations[con_loc] = con_quant
                else:
                    del_list.append(con_loc)
            for dl in del_list:
                del consignee_locations[dl]

            for con_data in consignee_locations:
                con_id = self.env['res.partner'].browse(con_data)
                temp_id = self.env.ref('aspl_consignee_management.product_expiry_alert_mail')
                temp_id.with_context({'email_to': con_id.email,
                                      'con_data': consignee_locations[con_data]}).send_mail(
                    con_id.id, force_send=True)


class StockConsigneeTransferLine(models.Model):
    _name = 'stock.consignee.transfer.line'
    _description = 'Consignee Transfer Line'

    consignee_record_id = fields.Many2one('stock.consignee.transfer',
                                          string="Consignee Ref")
    product_id = fields.Many2one('product.product', string="Product")
    requested_qty = fields.Float(string="Requested Qty", default="1")
    transfer_qty = fields.Float(string="Transferred Qty")
    uom_id = fields.Many2one(related='product_id.uom_id', store=True, string="Unit Of Measure")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
