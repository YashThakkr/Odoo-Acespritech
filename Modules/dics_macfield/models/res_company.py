from odoo import fields, api, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    footer1 = fields.Text(
        string="Footer 1"
    )
    footer2 = fields.Text(
        string="Footer 2"
    )
    chinese_name = fields.Char(
        string="Chinese Name"
    )
    fax = fields.Char(
        string="Fax"
    )
    ac_phone = fields.Char(
        string="A/C Phone"
    )
    ac_fax = fields.Char(
        string="A/C Fax"
    )
