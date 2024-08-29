from odoo import api, fields, models, _


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    uom_po_id = fields.Many2one('uom.uom', related='product_id.uom_po_id', readonly=True)
