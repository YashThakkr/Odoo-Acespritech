import datetime
import dateutil.parser
from odoo import api, fields, models, _
from datetime import timedelta, date


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cus_po = fields.Char(
        string="Cus P/O"
    )
    product_size = fields.Char(
        string="Pack Size"
    )
    product_moq = fields.Char(
        string="MOQ"
    )
    storage_con = fields.Selection([
        ('ambient', 'Ambient常溫'),
        ('Chilled', 'Chilled冷藏0-4°C'),
        ('Frozen', 'Frozen冷凍-18°C')],
        string="Storage Condition"
    )
    shelf_life = fields.Char(
        string="Shelf Life"
    )
    weight = fields.Float(
        string="Net Weight"
    )
    categ_id = fields.Many2one(
        "product.category",
        string="Category "
    )
    product_uom_qty = fields.Float(
        string="Qty",
        compute='_compute_product_uom_qty',
        digits='Quantity', default=1,
        store=True, readonly=False, required=True, precompute=True
    )
    customer_lead = fields.Float(
        string="Lead Time",
        compute='_compute_customer_lead',
        digits='Quantity',
        store=True, readonly=False, required=True, precompute=True,
        help="Number of days between the order confirmation and the shipping of the products to the customer")

    @api.onchange('product_template_id')
    def _onchange_dics(self):
        if self.product_template_id:
            self.product_size = self.product_template_id.product_size
            self.product_moq = self.product_template_id.product_moq
            self.storage_con = self.product_template_id.storage_con
            self.shelf_life = self.product_template_id.shelf_life
            self.weight = self.product_template_id.weight
            self.categ_id = self.product_template_id.categ_id

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        for line in self:

            if line.cus_po:
                res['cus_po'] = line.cus_po
        return res

    line_discount = fields.Float(
        string='Computed Field',
        compute='_compute_total_custom_discount',
        store=True
    )

    @api.depends('price_unit', 'product_uom_qty', 'price_subtotal')
    def _compute_total_custom_discount(self):
        for record in self:
            record.line_discount = record.price_unit * record.product_uom_qty - record.price_subtotal
            if record.price_unit < 0:
                record.line_discount = abs(record.price_unit + record.line_discount)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    operator_id = fields.Many2one(
        comodel_name='res.users',
        string="Operator",
        store=True,
        default=lambda self: self.env.user,
    )
    commitment_date = fields.Datetime(
        default=lambda self: fields.Date.to_string(fields.Date.context_today(self) + timedelta(days=1)),

    )
    route = fields.Char(
        string="Route"
    )
    opening_hours = fields.Char(
        string="Opening Hours"
    )

    def _create_invoices(self, grouped=False,commitment_date=False, final=False, date=None,route=False,opening_hours=False):
        result = super(SaleOrder, self)._create_invoices(opening_hours,commitment_date, route)
        for order in self:
            result.update({
                'commitment_date': order.commitment_date,
                'route': order.route,
                'opening_hours': order.opening_hours,
            })

        return result

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

    # def create_invoice(self):
    #     res = super(SaleOrder, self).create_invoice()
    #     invoices = self.env['account.move']
    #     for order in self:
    #         # Create the invoice
    #         invoice = invoices.create({
    #             'partner_id': order.partner_id.id,
    #             'route': order.partner_id.route,
    #             # Include other necessary fields for the invoice
    #         })
    #     return res

    def _prepare_invoice(self, **optional_values):
        res = super(SaleOrder, self)._prepare_invoice()
        for line in self:
            if line.operator_id.id:
                res['invoice_operator_id'] = line.operator_id.id
        return res
    
    
#     @api.depends('partner_id')
#     def _compute_partner_invoice_id(self):
#         for order in self:
#             order.partner_invoice_id = False
#             #order.partner_invoice_id = order.partner_id.address_get(['invoice'])['invoice'] if order.partner_id else False
    
    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for order in self:
            order.partner_shipping_id = False
            #order.partner_shipping_id = order.partner_id.address_get(['delivery'])['delivery'] if order.partner_id else False
                
    @api.onchange("date_order")
    def onchange_date_order(self):
        for rec in self:
            if rec.date_order:
                rec.validity_date = rec.date_order + timedelta(days=30)
            else:
                rec.date_order = date.today()

    def open_discount_product_wizard(self):
        return {
            'name': 'Discount Product',
            'type': 'ir.actions.act_window',
            'res_model': 'service.product.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('dics_macfield.service_product_wizard_form_view').id,
            'target': 'new',
        }

    total_line_discount = fields.Monetary(
        string='Discount',
        compute='_compute_order_total_custom_discount'
    )

    @api.depends('order_line.line_discount')
    def _compute_order_total_custom_discount(self):
        for order in self:
            order.total_line_discount = sum(order.order_line.mapped('line_discount'))
