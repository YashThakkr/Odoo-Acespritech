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


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_consignee = fields.Boolean(string="Consignee")

    @api.model_create_multi
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        if res.is_consignee and self.env['ir.config_parameter'].sudo().get_param(
                'aspl_consignee_management.is_create_location', False):
            location_id = self.env['stock.location'].create(
                {'name': res.name + '/stock', 'usage': 'internal'})
            if location_id:
                res.partner_id.update({"location_id": location_id.id, 'is_consignee': True})
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_consignee = fields.Boolean(string="Consignee")
    location_id = fields.Many2one('stock.location', string="Location",
                                  domain="[('usage', '=', 'internal')]")

    @api.model_create_multi
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if res.is_consignee and self.env['ir.config_parameter'].sudo().get_param(
                'aspl_consignee_management.is_create_location', False):
            location_id = self.env['stock.location'].create(
                {'name': res.name + '/stock', 'usage': 'internal'})
            if location_id:
                res.update({"location_id": location_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
