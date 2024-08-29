# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # branch_ids = fields.One2many('company.branch', 'company_id', string='Branches')
    # branch_id = fields.Many2one('company.branch', string='Branch', default=lambda self: self.env.user.get_current_branch())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
