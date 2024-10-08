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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rating = fields.Float()
    float_rating = fields.Float(store=True)

    def write_rating(self, args):
        self.float_rating = args.get('float_rating')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
