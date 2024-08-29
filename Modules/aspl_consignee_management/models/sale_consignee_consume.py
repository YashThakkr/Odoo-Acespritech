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

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ConsigneeConsumeItems(models.Model):
    _name = 'consignee.consume.items'
    _description = 'Consume Items'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Partner",
                                 domain=[('is_consignee', '=', True)])
    sale_id = fields.Many2one('sale.order', string="Sale")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
    ], default='draft', string="State", tracking=True)
    date = fields.Datetime(string="Date")
    customers_consignee_line = fields.One2many('customers.consignee.items.lines',
                                               'customers_consignee_id',
                                               string="Customers Consignee Lines")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order Ref")
    so_number_ref = fields.Char(related="sale_order_id.name", store=True,
                                string="Sale Order Number")

    @api.model
    def default_get(self, field_list):
        res = super(ConsigneeConsumeItems, self).default_get(field_list)
        res.update({'partner_id': self.env.user.partner_id.id, 'date': datetime.today()})
        return res

    @api.model_create_multi
    def create(self, vals):
        for rec in vals:
            rec['name'] = self.env['ir.sequence'].next_by_code(
                'aspl_consignee_management.sequence_consignee_consume_items')
        return super(ConsigneeConsumeItems, self).create(vals)

    def action_confirm(self):
        self.ensure_one()
        if not self.customers_consignee_line:
            raise ValidationError(_('Please enter lines first!'))
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def action_done(self):
        self.ensure_one()
        line_lst = []
        for line in self.customers_consignee_line:
            line_lst.append((0, 0, {
                'name': line.product_id.name,
                'price_unit': line.product_id.lst_price,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id and line.product_id.uom_id.id or False,
                'product_uom_qty': line.consumed_qty}))
        if line_lst:
            sale_obj = self.env['sale.order']
            fields = []
            sale_vals = sale_obj.default_get(fields)
            sale_vals.update(
                {'partner_id': self.partner_id.id, 'origin': self.name, 'order_line': line_lst})
            sale_id = sale_obj.create(sale_vals)
            if sale_id:
                self.write({'sale_order_id': sale_id.id, 'state': 'done'})
                create_sale_state = self.env['ir.config_parameter'].sudo().get_param(
                    'aspl_consignee_management.is_create_sale_order')
                if create_sale_state:
                    sale_id.action_confirm()
                send_mail = self.env['ir.config_parameter'].sudo().get_param(
                    'aspl_consignee_management.is_send_mail')
                if send_mail:
                    template_id = self.env.ref(
                        'aspl_consignee_management.consume_items_order_template')
                    template_id.send_mail(self.id, force_send=True)
        return True

    def open_sale_order(self):
        if self.sale_order_id:
            view_id = self.env.ref('sale.view_order_form').id
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'view_id': view_id,
                'res_id': self.sale_order_id.id,
            }


class CustomersConsigneeItemsLines(models.Model):
    _name = 'customers.consignee.items.lines'
    _description = 'Consignee Items Lines'

    customers_consignee_id = fields.Many2one('consignee.consume.items')
    product_id = fields.Many2one('product.product', string="Product")
    consumed_qty = fields.Float(string="Consumed Qty", default="1")
    uom_id = fields.Many2one(related='product_id.uom_id', store=True, string="Unit Of Measure")

    @api.constrains('consumed_qty')
    def check_transfer_qty(self):
        for each in self:
            if each.consumed_qty == 0:
                raise ValidationError(_('Consumed quantity is greater than zero!'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
