# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    signature = fields.Image('Signature', help='Signature received through the portal.',
                             copy=False, attachment=True,
                             max_width=1024, max_height=1024)
    signed_by = fields.Char('Signed By', help='Name of the person that signed the Invoice.', copy=False)
    signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: