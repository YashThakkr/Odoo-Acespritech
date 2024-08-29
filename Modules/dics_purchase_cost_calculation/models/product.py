# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_cost_price = fields.Float('Purchase Cost Price')
    po_uom_name = fields.Char(string='Purchase Unit of Measure Name', related='uom_po_id.name', readonly=True)
    po_uom_categ_id = fields.Many2one('uom.category', related='uom_po_id.category_id', readonly=True, required=True)


    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if self._context.get('_import_current_module', ''):
            if 'purchase_cost_price' in vals:
                self.purchase_cost_price_update()
        return res

    def purchase_cost_price_update(self):
        if self.uom_id.id == self.uom_po_id.id:
            self.standard_price = self.purchase_cost_price
        if self.uom_id.id != self.uom_po_id.id:
            po_cost_price = self.purchase_cost_price
            for uom in self.po_uom_categ_id.uom_ids:
                po_cost_price = po_cost_price / uom.ratio
                if uom.name == self.uom_po_id.name and uom.uom_type == 'reference':
                    break
            self.standard_price = po_cost_price


    @api.onchange('purchase_cost_price', 'uom_po_id', 'uom_id')
    def _onchange_purchase_cost_price(self):
        if self.uom_id.id == self.uom_po_id.id:
            self.standard_price = self.purchase_cost_price
        if self.uom_id.id != self.uom_po_id.id:
            po_cost_price = self.purchase_cost_price
            for uom in self.po_uom_categ_id.uom_ids:
                po_cost_price = po_cost_price / uom.ratio
                if uom.name == self.uom_po_id.name and uom.uom_type == 'reference':
                    break
            self.standard_price = po_cost_price


