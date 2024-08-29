from odoo import models, fields, api, _


class DuplicateWiz(models.TransientModel):
    _name = 'duplicate.wiz'
    _description = 'Duplicate Wizard'

    so_ids = fields.Many2many('sale.order','sale_order_id',
                                      string='so ids',readonly=True)


    def action_save(self):
        for sale in self.so_ids.browse(self.env.context['active_ids']):
            print('111111111112', self.so_ids.browse(self.so_ids.env.context))
            sale.copy()

