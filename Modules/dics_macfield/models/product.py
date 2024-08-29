from odoo import api, fields, models,exceptions, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_size = fields.Char(
        string="Size"
    )
    product_moq = fields.Char(
        string="MOQ"
    )
    storage_con = fields.Selection(
        [('ambient', 'Ambient常溫'),
         ('Chilled', 'Chilled冷藏0-4°C'),
         ('Frozen', 'Frozen冷凍-18°C')],
        string="Storage Condition"
    )
    shelf_life = fields.Char(
        string="Shelf Life"
    )
    category_id = fields.Many2one(
        "uom.category",
        "Product UOM Category",
        related="uom_id.category_id"
    )


    @api.onchange('default_code')
    def _onchange_default_code(self):
        if not self.default_code:
            return

        domain = [('default_code', '=', self.default_code)]
        if self.id.origin:
            domain.append(('id', '!=', self.id.origin))

        # if self.env['product.template'].search(domain, limit=1):
        #     return {'warning': {
        #         'title': _("Note:"),
        #         # 'message': _("The Internal Reference '%s' already exists.", self.default_code),
        #     }}

    @api.model
    def create(self, vals):
        if 'default_code' in vals and vals['default_code']:
            duplicate_products = self.search([('default_code', '=', vals['default_code'])])
            if duplicate_products:
                raise exceptions.UserError(_('Internal reference is duplicate'))
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        if 'default_code' in vals and vals['default_code']:
            duplicate_products = self.search([
                ('default_code', '=', vals['default_code']),
                ('id', '!=', self.id),
            ])
            if duplicate_products:
                raise exceptions.UserError(_('Internal reference is duplicate'))
        return super(ProductTemplate, self).write(vals)
    
    # _sql_constraints = [(
    #     'unique_default_code',
    #     'UNIQUE(default_code)',
    #     "The Internal Reference already exists."
    # )]

    # @api.constrains('default_code')
    # def _check_internal_reference_uniqueness(self):
    #     for product in self:
    #         if product.default_code:
    #             duplicate_products = self.search([
    #                 ('default_code', '=', product.default_code),
    #                 ('id', '!=', product.id),
    #             ])
    #             if duplicate_products:
    #                 raise exceptions.UserExrror("Internal reference  is duplicate")



class ProductProduct(models.Model):
    _inherit = 'product.product'

    category_id = fields.Many2one(
        "uom.category",
        "Product UOM Category",
        related="uom_id.category_id"
    )


    @api.onchange('default_code')
    def _onchange_default_code(self):
        if not self.default_code:
            return

        domain = [('default_code', '=', self.default_code)]
        if self.id.origin:
            domain.append(('id', '!=', self.id.origin))

        # if self.env['product.template'].search(domain, limit=1):
        #     return {'warning': {
        #         'title': _("Note:"),
        #         'message': _("The Internal Reference '%s' already exists.", self.default_code),
        #     }}

    # _sql_constraints = [(
    #     'unique_default_code',
    #     'UNIQUE(default_code)',
    #     "The Internal Reference already exists."
    # )]
    @api.model
    def create(self, vals):
        if 'default_code' in vals and vals['default_code']:
            duplicate_products = self.search([('default_code', '=', vals['default_code'])])
            if duplicate_products:
                raise exceptions.UserError(_('Internal reference is duplicate'))
        return super(ProductProduct, self).create(vals)

    def write(self, vals):
        if 'default_code' in vals and vals['default_code']:
            duplicate_products = self.search([
                ('default_code', '=', vals['default_code']),
                ('id', '!=', self.id),
            ])
            if duplicate_products:
                raise exceptions.UserError(_('Internal reference is duplicate'))
        return super(ProductProduct, self).write(vals)

    # @api.constrains('default_code')
    # def _check_internal_reference_uniqueness(self):
    #     for product in self:
    #         if product.default_code:
    #             duplicate_products = self.search([
    #                 ('default_code', '=', product.default_code),
    #                 ('id', '!=', product.id),
    #             ])
    #             if duplicate_products:
    #                 raise exceptions.UserError('Internal reference is duplicate')

