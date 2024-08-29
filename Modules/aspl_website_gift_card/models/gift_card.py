# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#################################################################################

import time, datetime
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode
from odoo import models, fields, api
from odoo.http import request


class WebsiteGiftCard(models.Model):
    _name = "website.gift.card"
    _description = "Website Gift Card"
    _rec_name = "card_no"

    def random_cardno(self):
        return int(time.time())

    card_no = fields.Char(string="Card No", default=random_cardno, readonly=True)
    card_value = fields.Float(string="Card Value")
    customer_id = fields.Many2one('res.partner', string="Customer")
    issue_date = fields.Date(string="Issue Date", default=datetime.datetime.now().date())
    expire_date = fields.Date(string="Expire Date")
    pin_no = fields.Integer(string="Pin No.")
    is_active = fields.Boolean('Active', default=True)
    used_line = fields.One2many('gift.card.use', 'card_id', string="Used Line")
    recharge_line = fields.One2many('gift.card.recharge', 'card_id', string="Recharge Line")
    encrypted_id = fields.Char(string='Encrypted Id')
    email = fields.Char(string="Email")
    user_name = fields.Char(string="User Name")

    @api.model
    def create(self, vals):
        if vals.get('card_value') > 0:
            res = super(WebsiteGiftCard, self).create(vals)
            message = str(res['id'])
            key = Fernet.generate_key()
            request.session['encryption_key'] = key
            f = Fernet(key)
            cipher = f.encrypt(str(message).encode())
            encoded_cipher = b64encode(cipher)
            res['encrypted_id'] = encoded_cipher
            template_id = self.env['ir.model.data'].check_object_reference(
                'aspl_website_gift_card', 'email_template__buy_card')
            if template_id and template_id[1]:
                template_obj = self.env['mail.template'].browse(template_id[1])
                template_obj.send_mail(res.id, force_send=True)
            return res


class GiftCardUse(models.Model):
    _name = 'gift.card.use'
    _description = 'Gift Card Use'

    card_id = fields.Many2one('website.gift.card', string="Card", readonly=True)
    order_id = fields.Many2one("sale.order", string="Order")
    order_date = fields.Date(string="Order Date")
    amount = fields.Float(string="Amount")


class GiftCardRecharge(models.Model):
    _name = 'gift.card.recharge'
    _description = 'Gift Card Recharge'

    card_id = fields.Many2one('website.gift.card', string="Card", readonly=True)
    amount = fields.Float(string="amount")

    @api.model_create_multi
    def create(self, vals):
        res = super(GiftCardRecharge, self).create(vals)
        template_id = self.env['ir.model.data'].check_object_reference('aspl_website_gift_card',
                                                                       'email_template_recharge_card')
        if template_id and template_id[1]:
            template_obj = self.env['mail.template'].browse(template_id[1])
            template_obj.send_mail(res.id, force_send=True)

        return res


class Product(models.Model):
    _inherit = 'product.product'

    is_gift_card = fields.Boolean(string="is gift card")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def write(self, vals):
        return super(SaleOrderLine, self).write(vals)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    gift_card_value = fields.Float(string="Gift Card Amount")
    gift_card_id = fields.Many2one('website.gift.card', string="Gift Card")
    gift_card_use_ids = fields.One2many('gift.card.use', 'order_id', string="Gift Card Use")
    receiver_email = fields.Char(string="Receiver Email")
    receiver_name = fields.Char(string="Receiver Name")

    def write(self, vals):
        for so in self:
            if vals.get('state') == 'sale' or vals.get('state') == 'done':
                sale_order_line_id = self.env['sale.order.line'].search([('order_id', '=', so.id),
                                                                         ('product_id.is_gift_card', '=', True)])
                if sale_order_line_id:
                    if not so.gift_card_id:
                        qty = sale_order_line_id.product_uom_qty
                        gift_card_value = sale_order_line_id.price_subtotal / qty
                        while qty > 0:
                            gift_card_obj = self.env['website.gift.card']
                            gift_card_obj.create({
                                'card_value': gift_card_value,
                                'customer_id': int(self.env.context.get('partner_id'))
                                if self.env.context.get('from_wizard') else self.env.user.partner_id.id,
                                'email': 'admin',
                                'user_name': 'admin'
                            })
                            qty -= 1
                            time.sleep(2)
                    if so.gift_card_id:
                        gift_card_obj = self.env['website.gift.card'].search([('id', '=', so.gift_card_id.id)])
                        if gift_card_obj:
                            gift_card_obj.write({
                                'card_value': gift_card_obj.card_value + sale_order_line_id.price_subtotal,
                            })
                        self.env['gift.card.recharge'].create({
                            'card_id': so.gift_card_id.id,
                            'amount': sale_order_line_id.price_subtotal
                        })
            res = super(SaleOrder, self).write(vals)
            return res

    def _recompute_prices(self):
        lines_to_recompute = self.order_line.filtered(lambda line: not line.display_type and not line.product_id.is_gift_card)
        lines_to_recompute._compute_price_unit()
        lines_to_recompute.discount = 0.0
        lines_to_recompute._compute_discount()
        self.show_update_pricelist = False


class GiftCardValue(models.Model):
    _name = 'gift.card.value'
    _description = 'Gift Card Value'
    _rec_name = 'amount'

    active = fields.Boolean(string="Active", default=True)
    amount = fields.Float(string="Amount")
    sequence = fields.Integer(string="Sequence")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
