from odoo import api, fields, models, exceptions, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    route = fields.Char(
        string="Route"
    )
    fax = fields.Char(
        string="Fax"
    )
    opening_hours = fields.Char(
        string="Opening Hours"
    )
    multiple_invoice = fields.Boolean(
        string="Multiple Invoice"
    )
    chinese = fields.Char(
        string='Chinese Field'
    )
    contact = fields.Char(
        string="Contact"
    )
    customer_code = fields.Char(
        string="Customer Code"
    )
    # _sql_constraints = [(
    #     'unique_customer_code',
    #     'UNIQUE(customer_code)',
    #     "Customer Code is duplicate"
    # )]

    @api.constrains('customer_code')
    def _check_customer_code_uniqueness(self):
        for res in self:
            if res.customer_code:
                duplicate_res = self.search([
                    ('customer_code', '=', res.customer_code),
                    ('id', '!=', res.id),
                ])
                if duplicate_res:
                    raise exceptions.UserError('Customer Code is duplicate')
