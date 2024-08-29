# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    phone = fields.Char(string='Phone')
    fax = fields.Char(string='Fax')
