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

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def generate_serial_nos(self):
        self.ensure_one()
        for pack in self.move_ids:
            pack.generate_serial_lot()


class StockMove(models.Model):
    _inherit = "stock.move"

    def generate_serial_lot(self):
        self.ensure_one()
        if self.product_uom_qty == self.quantity_done:
            if self.move_line_ids:
                for each in self.move_line_ids:
                    serial_no = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                    each.write({'lot_name': serial_no})

        elif self.product_uom_qty != self.quantity_done and self.quantity_done != 0:
            qty_lot = self.product_uom_qty - self.quantity_done
            if self.product_id.tracking == 'lot':
                if self.move_line_ids:
                    for each in self.move_line_ids:
                        serial_no = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                        each.write({'lot_name': serial_no})
                if qty_lot:
                    serial_no = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                    self.env['stock.move.line'].create({
                        'lot_name': serial_no,
                        'reserved_uom_qty': qty_lot,
                        'qty_done': qty_lot,
                        'product_uom_id': self.product_id.uom_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'move_id': self.id,
                        'product_id': self.product_id.id})

            elif self.product_id.tracking == 'serial':
                if self.move_line_ids:
                    for each in self.move_line_ids:
                        serial_no = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                        each.write({'lot_name': serial_no})
                if qty_lot:
                    for each in range(int(qty_lot)):
                        serial_no = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                        self.env['stock.move.line'].create({
                            'lot_name': serial_no,
                            'reserved_uom_qty': 1.0,
                            'qty_done': 1.0,
                            'product_uom_id': self.product_id.uom_id.id,
                            'location_id': self.location_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'move_id': self.id,
                            'product_id': self.product_id.id})

        else:
            qty_lot = self.product_uom_qty - self.quantity_done
            if self.product_id.tracking == 'lot':
                if self.move_line_ids:
                    for each in self.move_line_ids:
                        serial_no = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                        each.write({'lot_name': serial_no, 'reserved_uom_qty': qty_lot,
                                    'qty_done': qty_lot, 'product_uom_id': self.product_id.uom_id.id,
                                    'location_id': self.location_id.id, 'location_dest_id': self.location_dest_id.id})
                else:
                    serial_no = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                    self.env['stock.move.line'].create({
                        'lot_name': serial_no,
                        'reserved_uom_qty': qty_lot,
                        'qty_done': qty_lot,
                        'product_uom_id': self.product_id.uom_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'move_id': self.id,
                        'product_id': self.product_id.id})
                self.write({
                    'quantity_done': qty_lot
                })

            elif self.product_id.tracking == 'serial':
                if self.move_line_ids:
                    for each in self.move_line_ids:
                        serial_no = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                        each.write({'lot_name': serial_no, 'reserved_uom_qty': 1,
                                    'qty_done': 1, 'product_uom_id': self.product_id.uom_id.id,
                                    'location_id': self.location_id.id, 'location_dest_id': self.location_dest_id.id})
                else:
                    for each in range(int(self.product_uom_qty)):
                        serial_no = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                        self.env['stock.move.line'].create({
                            'lot_name': serial_no,
                            'reserved_uom_qty': 1.0,
                            'qty_done': 1.0,
                            'product_uom_id': self.product_id.uom_id.id,
                            'location_id': self.location_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'move_id': self.id,
                            'product_id': self.product_id.id})


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_type_code = fields.Selection(related='picking_id.picking_type_code', string="code")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
