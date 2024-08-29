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
from odoo import api, fields, models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def default_get(self, fields):
        if self.env.context.get('return_picking_id'):
            context = dict(self.env.context)
            context.update({'active_id': self.env.context.get('return_picking_id'),
                            'active_ids': [self.env.context.get('return_picking_id')],
                            'active_model': 'stock.picking'})
            self.env.context = context
        res = super(StockReturnPicking, self).default_get(fields)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
