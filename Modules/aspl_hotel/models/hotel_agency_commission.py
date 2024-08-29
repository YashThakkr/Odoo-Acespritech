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


class HotelAgencyCommission(models.Model):
    _name = "hotel.agency.commission"
    _description = "Hotel Agency Commission"
    _rec_name = 'walk_in_id'

    walk_in_id = fields.Many2one('walk.in.detail', string="Customer", required=True)
    agency_id = fields.Many2one('res.partner', string="Agency", required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('cancel', 'Cancel')], string="State")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
