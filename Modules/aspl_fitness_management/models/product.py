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

from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_gym_service = fields.Boolean("Is Gym Service")
    exercise_ids = fields.One2many("gym.exercise", 'service_id', string='Exercise')
    is_equipment = fields.Boolean("Is Equipment")
    is_membership = fields.Boolean("Is Membership")
    membership_period = fields.Integer("Membership Period")
    membership_period_type = fields.Selection(
        [('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')],
        string="Period Type",
        default="days")
    branch_id = fields.Many2one('company.branch', string="Branch",
                                default=lambda self: self.env.user.branch_id)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_gym_service = fields.Boolean("Is Gym Service")
    exercise_ids = fields.One2many('gym.exercise', 'service_tmpl_id', string="Exercises")
    is_equipment = fields.Boolean("Is Equipment")
    is_membership = fields.Boolean("Is Membership")
    membership_period = fields.Integer("Membership Period")
    membership_period_type = fields.Selection(
        [('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')],
        string="Period Type",
        default="days")
    branch_id = fields.Many2one('company.branch', string="Branch")

    @api.model
    def default_get(self, field_list):
        result = super(ProductTemplate, self).default_get(field_list)

        if self._context.get('fitness_categ'):
            categ_dict = {'company_id': self.env.company.id,
                          'branch_id': self.env.user.branch_id.id}

            if self._context.get('gym_service') and 'company_id' in field_list:
                categ_dict['categ_id'] = self.env.ref('product.product_category_3').id
            elif self._context.get('gym_equipment') and 'company_id' in field_list:
                categ_dict['categ_id'] = self.env.ref(
                    'aspl_fitness_management.gym_equipment_category').id
            elif self._context.get('fitness_membership') and 'company_id' in field_list:
                categ_dict['categ_id'] = self.env.ref(
                    'aspl_fitness_management.gym_membership_category').id

            result.update(categ_dict)
        return result


class EquipmentMaintenance(models.Model):
    _name = 'equipment.maintenance'
    _description = 'Equipment Maintenance'

    name = fields.Char("Name")
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.company)
    branch_id = fields.Many2one('company.branch', string="Branch")
    date_dispatch = fields.Date("Dispatch Date")
    equipment_line_ids = fields.One2many('equipment.maintenance.line', 'maintenance_id',
                                         string="Maintenance Lines")
    location_id = fields.Many2one('stock.location', string="Location")
    paid_maintenance = fields.Boolean("Paid Maintenance")
    picking_ids = fields.One2many('stock.picking', 'maintenance_id', string="Stock")
    send_to_vendor_location = fields.Boolean("Send To Vendor Location")
    invoice_id = fields.Many2one('account.move', string="Invoice")
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('returned', 'Returned'),
         ('cancel', 'Cancel')],
        string="State", default="draft")

    def button_confirm(self):
        equipment_lot_ids = [each.lot_id.id for each in self.equipment_line_ids]
        quant_ids = self.env['stock.quant'].search([('lot_id', 'in', equipment_lot_ids),
                                                    ('location_id', '=',
                                                     self.branch_id.stock_location_id.id)])
        if not self.equipment_line_ids:
            raise ValidationError(_('Add atleast one equipment line to confirm'))
        if any(self.equipment_line_ids.filtered(lambda line: line.qty <= 0)):
            raise ValidationError(_("Equipment quantity must be greater than zero"))
        if not quant_ids:
            raise ValidationError(_('Lot location of equipment must be same'
                                    ' as branch stock location.'))
        move_lst = []
        warehouse_id = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)],
            order="id ASC", limit=1)
        if self.send_to_vendor_location:
            picking_type_id = self.env['stock.picking.type'].search(
                [('warehouse_id', '=', warehouse_id.id),
                 ('code', '=', 'outgoing')], order="id ASC",
                limit=1)
            picking_type_rec = picking_type_id if picking_type_id else self.env.ref(
                'stock.picking_type_out')
            location_id = self.branch_id.stock_location_id
            location_dest_id = self.env.ref('stock.stock_location_suppliers')
        else:
            picking_type_id = self.env['stock.picking.type'].search(
                [('warehouse_id', '=', warehouse_id.id),
                 ('code', '=', 'internal')], order="id ASC",
                limit=1)
            picking_type_rec = picking_type_id if picking_type_id else self.env.ref(
                'stock.picking_type_internal')
            location_id = self.branch_id.stock_location_id
            location_dest_id = self.branch_id.service_location_id
        for each in self.equipment_line_ids:
            move_lst.append((0, 0, {'product_id': each.product_id.id,
                                    'name': each.product_id.partner_ref,
                                    'product_uom': each.product_id.uom_id.id,
                                    'product_uom_qty': each.qty,
                                    'location_id': location_id.id if location_id else False,
                                    'location_dest_id': location_dest_id.id if location_dest_id else False,
                                    'lot_ids': [(6, 0, each.lot_id.ids)] if each.lot_id else [],
                                    }))
        picking_id = self.env['stock.picking'].create({
            'picking_type_id': picking_type_rec.id,
            'partner_id': self.vendor_id.id,
            'date': fields.Datetime.today().date(),
            'origin': '',
            'location_id': location_id.id if location_id else False,
            'location_dest_id': location_dest_id.id if location_dest_id else False,
            'company_id': self.env.company.id,
            'move_ids_without_package': move_lst,
        })
        picking_id.action_assign()
        picking_id.button_validate()
        immediate_transfer = self.env['stock.immediate.transfer'].create(
            {'pick_ids': [(4, picking_id.id)]})
        immediate_transfer.process()
        self.write({'picking_ids': [(4, picking_id.id)],
                    'state': 'confirmed'})

    def button_return_picking(self):
        picking_id = self.env['stock.picking'].browse(min(self.picking_ids.ids)) if len(
            self.picking_ids.ids) > 0 else False
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.return.picking',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Return Picking',
            'view_id': self.env.ref('stock.view_stock_return_picking_form').id,
            'context': {'return_picking_id': picking_id.id if picking_id else False,
                        'maintenance_id': self.id if self else False}
        }
        return action

    def button_create_invoice(self):
        if self.paid_maintenance:
            lst = []

            for each in self.equipment_line_ids:
                lst.append((0, 0, {'name': each.product_id.name,
                                   'price_unit': each.product_id.lst_price,
                                   'product_id': each.product_id.id,
                                   'quantity': each.qty,
                                   'branch_id': self.branch_id.id
                                   }))
            res = self.env['account.move'].create({'partner_id': self.vendor_id.id,
                                                   'branch_id': self.branch_id.id,
                                                   'invoice_date': date.today(),
                                                   'invoice_line_ids': lst,
                                                   'move_type': 'in_invoice',
                                                   })
            res.action_post()
            self.invoice_id = res.id

    def button_sent_invoice(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref('aspl_fitness_management.email_template_equipment_invoice')
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_to_res_id(
                'mail.email_compose_message_wizard_form')
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        if template_id and template_id.lang:
            lang = template_id._render_lang(self.invoice_id.ids).get(self.invoice_id.id)
        else:
            lang = lang.code
        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.invoice_id.id,
            'default_use_template': bool(template_id.id) if template_id else False,
            'default_template_id': template_id.id if template_id else False,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'maintenance_id': self.id,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'model_description': self.invoice_id.with_context(lang=lang).type_name,
            'force_email': True
        }
        dict = {
            'name': 'Send Invoice',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        return dict


class EquipmentMaintenanceLine(models.Model):
    _name = 'equipment.maintenance.line'
    _description = 'Equipment Maintenance Line'
    _rec_name = 'maintenance_id'

    description = fields.Char("Description")
    product_id = fields.Many2one('product.product', string="Product",
                                 domain="[('is_equipment','=',True)]")
    lot_id = fields.Many2one('stock.production.lot', string="Lot")
    maintenance_id = fields.Many2one('equipment.maintenance', string="Maintenance")
    qty = fields.Float("Qty")
    return_qty = fields.Float("Return Qty")

    @api.onchange('product_id')
    def _onchange_product(self):
        for each in self:
            each.description = each.product_id.description if each.product_id else ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
