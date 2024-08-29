from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    collection_hrs = fields.Char(
        string='Collection hours:',
        default='09:00-13:00/ 14:00-17:30 (Monday - Sunday)',
    )
    route = fields.Char(
        string="Route"
    )
    opening_hours = fields.Char(
        string="Opening Hours"
    )
    partner_id = fields.Many2one('res.partner', domain="[('is_company', '=', True)]")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.route:
            self.route = self.partner_id.route
        else:
            self.route = False
        if self.partner_id.opening_hours:
            self.opening_hours = self.partner_id.opening_hours
        else:
            self.opening_hours = False
        if self.partner_id:
            self.partner_ref = self.partner_id.chinese
