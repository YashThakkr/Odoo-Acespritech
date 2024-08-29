from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cus_po = fields.Char(
        string="Cus P/O"
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    remark = fields.Char(
        string="Remarks"
    )
    invoice_operator_id = fields.Many2one(
        comodel_name='res.users',
        string="Operator",
        store=True,
        default=lambda self: self.env.user,
    )
    route = fields.Char(
        string='Route'
    )
    opening_hours = fields.Char(
        string="Opening Hours"
    )
    commitment_date = fields.Datetime(
        "Delivery Date"
    )

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            partner_route = self.partner_id.route
            self.route = partner_route
