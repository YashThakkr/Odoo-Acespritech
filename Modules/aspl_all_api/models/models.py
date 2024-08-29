# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class aspl_all_api(models.Model):
#     _name = 'aspl_all_api.aspl_all_api'
#     _description = 'aspl_all_api.aspl_all_api'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

