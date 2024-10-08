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

from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())

    # @api.model_create_multi
    # def create(self, vals):
    #     res = super(StockWarehouse, self).create(vals)
    #     res.lot_stock_id.write({'branch_id': res.branch_id.id})
    #     res.view_location_id.write({'branch_id': res.branch_id.id})
    #     res.wh_input_stock_loc_id.write({'branch_id': res.branch_id.id})
    #     res.wh_output_stock_loc_id.write({'branch_id': res.branch_id.id})
    #     res.wh_pack_stock_loc_id.write({'branch_id': res.branch_id.id})
    #     res.wh_qc_stock_loc_id.write({'branch_id': res.branch_id.id})
    #     return res

    # def write(self, vals):
    #     res = super(StockWarehouse, self).write(vals)
    #     if vals.get('branch_id'):
    #         self.lot_stock_id.write({'branch_id': vals.get('branch_id')})
    #         self.view_location_id.write({'branch_id': vals.get('branch_id')})
    #         self.wh_input_stock_loc_id.write({'branch_id': vals.get('branch_id')})
    #         self.wh_output_stock_loc_id.write({'branch_id': vals.get('branch_id')})
    #         self.wh_pack_stock_loc_id.write({'branch_id': vals.get('branch_id')})
    #         self.wh_qc_stock_loc_id.write({'branch_id': vals.get('branch_id')})
    #     return res


class StockLocation(models.Model):
    _inherit = 'stock.location'

    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # branch_id = fields.Many2one(
    #     'company.branch', string="Branch", default=lambda self:
    #     self.env.user.get_current_branch(), states={
    #         'done': [('readonly', True)],
    #         'cancel': [('readonly', True)]})

    # @api.model_create_multi
    # def create(self, vals):
    #     if not vals.get('branch_id'):
    #         user_id = self.env['res.users'].browse(
    #             self.env.context.get('uid')) if self.env.context.get(
    #             'uid') else False
    #         if user_id:
    #             vals.update({'branch_id': user_id.branch_id.id})
    #     return super(StockPicking, self).create(vals)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    # def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name,
    #                            origin, company_id, values):
    #     res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom,
    #                                                         location_id, name,
    #                                                         origin, company_id, values)
    #     res.update({'branch_id': values.get('branch_id')})
    #     return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    # branch_id = fields.Many2one('company.branch', string="Branch")

    # def _get_new_picking_values(self):
    #     res = super(StockMove, self)._get_new_picking_values()
    #     res.update({'branch_id': self.branch_id.id})
    #     return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # branch_id = fields.Many2one('company.branch', string="Branch", related="move_id.branch_id")


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # branch_id = fields.Many2one(related='location_id.branch_id', string='Branch', store=True,
    #                             readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
