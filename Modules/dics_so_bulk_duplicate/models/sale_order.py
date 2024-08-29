from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # def action_duplicate_sale(self):
    #     for sale in self.browse(self.env.context['active_ids']):
    #         print('111111111112', self.browse(self.env.context['active_ids']))
    #         sale.copy()

    def action_duplicate_sale(self):
        print("11111111111111")
        return {
            'name': _('Confirmation'),
            'type': 'ir.actions.act_window',
            'res_model': 'duplicate.wiz',
            'view_mode': 'form',
            'view_id': self.env.ref('dics_so_bulk_duplicate.view_duplicate_wiz').id,
            'target': 'new'
        }
