from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Wizard call ------>
    def action_confirm_sale(self):
        print("11111111111111")
        return {
            'name': _('Confirmation'),
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.so.wiz',
            'view_mode': 'form',
            'view_id': self.env.ref('dics_so_bulk_confirm.view_confirm_wiz').id,
            'target': 'new'
        }

    #<------ direct button call ------->
        # def action_confirm_sale(self):
        #     for sales in self:
        #         sales.action_confirm()