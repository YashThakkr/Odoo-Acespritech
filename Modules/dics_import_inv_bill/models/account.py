# -*- coding: utf-8 -*-
from odoo import fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    document_date = fields.Date(string="Document Date")
    is_xlsx_data = fields.Boolean(string="Is Xlsx Date",defalse=False,copy=False)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    log = fields.Char(string="log")