from odoo import models, fields, api, _
from odoo.exceptions import UserError



class ConfirmSoWiz(models.TransientModel):
    _name = 'confirm.so.wiz'
    _description = 'Confirm Wiz'

    so_con_ids = fields.Many2many('sale.order', 'sale_orders_id',
                                  string='so con ids', readonly=True)

    def action_save(self):
        for sales in self.so_con_ids.browse(self.env.context['active_ids']):
            sales.action_confirm()
