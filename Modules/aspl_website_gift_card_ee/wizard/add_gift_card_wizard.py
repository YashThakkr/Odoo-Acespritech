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

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AddGiftCard(models.TransientModel):
    _name = 'add.gift.card'
    _description = 'Add Gift Card'
    _order = 'id desc'

    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    card_no = fields.Many2one('website.gift.card', string="Card No")
    pin_no = fields.Integer(string="Pin No")
    type = fields.Selection([('add_new', "Add New"), ('recharge', "Recharge")], default='add_new', string='Type')
    gift_card_value_id = fields.Many2one('gift.card.value', string="Amount")
    gift_card_qty = fields.Integer(string="Number of gift card")
    receiver_name = fields.Char(string="Receiver Name")
    amount = fields.Float(string="Amount")
    receiver_email = fields.Char(string="Receiver Email", required=True)

    def add_gift_card(self):
        if self.partner_id:
            product_id = int(
                self.env['ir.config_parameter'].sudo().get_param('aspl_website_gift_card_ee.product_id'))
            sale_order_id = False
            if self.type == 'add_new' and not self.card_no:
                sale_order_id = self.env['sale.order'].sudo().with_context(from_wizard=True, partner_id=self.partner_id.id). \
                    create({'partner_id': self.partner_id.id,
                            'order_line': [(0, 0, {'product_id': product_id,
                                                   'product_uom_qty': float(self.gift_card_qty),
                                                   'qty_delivered': float(self.gift_card_qty),
                                                   'price_unit': self.gift_card_value_id.amount,
                                                   'name': 'Gift Card',
                                                   'product_uom': self.env.ref('uom.product_uom_categ_unit').id})]
                            })
            else:
                if self.card_no.pin_no == self.pin_no:
                    sale_order_id = self.env['sale.order'].with_context(from_wizard=True,
                                                                        partner_id=self.partner_id.id). \
                        create({
                                'partner_id': self.partner_id.id,
                                'gift_card_id': self.card_no.id,
                                'order_line': [(0, 0, {'product_id': product_id,
                                                       'product_uom_qty': 1,
                                                       'qty_delivered': 1,
                                                       'price_unit': self.amount})]
                        })
                else:
                    raise UserError(_('Invalid Pin No'))
            sale_order_id.action_confirm()
            move_id = sale_order_id._create_invoices()
            move_id.action_post()
            payment_obj = self.env['account.payment']
            values = {
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': move_id.partner_id.id,
                'amount': move_id.amount_total,
                'ref': move_id.name,
                'currency_id': move_id.company_id.currency_id.id,
                'date': datetime.today(),
                'payment_method_id': self.env.ref(
                    'account.account_payment_method_manual_in').id,
            }
            payment = payment_obj.sudo().create(values)
            payment.sudo().action_post()
            move_line = self.env['account.move.line'].search([('payment_id', '=', payment.id),
                                                              ('account_id', '=',
                                                               payment.partner_id.property_account_receivable_id.id)])
            move_id.js_assign_outstanding_line(move_line.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
