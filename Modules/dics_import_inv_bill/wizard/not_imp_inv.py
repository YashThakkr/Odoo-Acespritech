# -*- coding: utf-8 -*-
from odoo import fields, models, _


class NotImpInvWiz(models.TransientModel):
    _name = 'not.imp.inv.wiz'
    _description = 'Import Invoice Wiz'

    not_import_inv = fields.Text(string="File", required=True)
