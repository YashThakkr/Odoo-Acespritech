# -*- coding: utf-8 -*-
from odoo import fields, models, _


class NotImpsoWiz(models.TransientModel):
    _name = 'not.imp.so.wiz'
    _description = 'Not Import Sale Order Wizard'

    not_import_so = fields.Text(string="File", required=True)
