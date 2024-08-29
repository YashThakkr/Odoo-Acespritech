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

from odoo import models, api, _


class sale_order(models.Model):
    _inherit = 'sale.order'

    def get_transaction(self, order):
        tx_id = self.env['payment.transaction'].sudo().search([('reference', '=', order.name)], limit=1)
        if tx_id:
            return tx_id.vpstxid
        return ''

    def get_status(self, order):
        tx_id = self.env['payment.transaction'].sudo().search([('reference', '=', order.name)], limit=1)
        if tx_id:
            return tx_id.status
        return ''

    def get_status_msg(self, order):
        tx_id = self.env['payment.transaction'].sudo().search([('reference', '=', order.name)], limit=1)
        if tx_id:
            return tx_id.status_detail
        return ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: