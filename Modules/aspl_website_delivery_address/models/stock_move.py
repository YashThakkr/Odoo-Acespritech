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

from odoo import models
from itertools import groupby
from operator import itemgetter


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        grouped_moves = groupby(sorted(self, key=lambda m: [f.id for f in m._key_assign_picking()]), key=lambda m: [m._key_assign_picking()])
        for group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*list(moves))
            new_picking = False
            # Could pass the arguments contained in group but they are the same
            # for each move that why moves[0] is acceptable
            picking = moves[0]._search_picking_for_assignation()
            if picking:
                if any(picking.partner_id.id != m.partner_id.id or
                        picking.origin != m.origin for m in moves):
                    # If a picking is found, we'll append `move` to its move list and thus its
                    # `partner_id` and `ref` field will refer to multiple records. In this
                    # case, we chose to  wipe them.
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
            else:
                new_picking = True
                move_data = []
                move_data_ids = []
                for move in moves:
                    move_data.append({'stock_move_id': move.id, 'partner_id': move.partner_id.id})
                move_data = sorted(move_data,
                                  key=itemgetter('partner_id'))
                for key, value in groupby(move_data,
                                          key=itemgetter('partner_id')):
                    filtered_move_ids = []
                    for k in value:
                        filtered_move_ids.append(k['stock_move_id'])
                    move_data_ids.append(filtered_move_ids)
                for each in move_data_ids:
                    moves = self.browse(each)
                    picking = Picking.create(moves._get_new_picking_values())
                    moves.write({'picking_id': picking.id})
                    moves._assign_picking_post_process(new=new_picking)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
