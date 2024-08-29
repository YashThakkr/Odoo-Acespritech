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

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class RoomAdvancePayment(models.TransientModel):
    _name = 'room.advance.payment'
    _description = 'Room Advance Payment'

    amount = fields.Float('Advance Payment Amount', digits=0)
    minimum_amount = fields.Float('Minimum Payment Amount', digits=0)

    def confirm_payment(self):
        if self.amount < self.minimum_amount:
            raise UserError(_("Amount must be greater than Minimum Payment Amount !!"))
        walk_in_id = self.env['walk.in.detail'].sudo().browse(self.env.context.get('active_id'))
        if walk_in_id:
            return walk_in_id.with_context(amount=self.amount).create_folio()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
