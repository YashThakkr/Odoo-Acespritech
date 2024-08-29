# -*- coding: utf-8 -*-
# Email: sales@creyox.com

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    report_options = fields.Selection(selection=[
        ('print', 'Always Print'),
        ('open', 'Always Open'),
        ('download', 'Always Download')
    ], string='Report Printing Option', default='print')

    def search_user_report_option(self,list):
        return self.env.user.report_options