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

import random
from datetime import datetime, date

from odoo.exceptions import ValidationError

from odoo import fields, models, api, _


class GiftVoucher(models.Model):
    _name = "gift.voucher.detail"
    _description = "Gift Voucher Details"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    expiry_date = fields.Date(string="Expiry Date", required=True)
    voucher_type = fields.Selection(
        [("order_total", "Order Total"), ("category", "Category")],
        default="order_total",
        string="Voucher Type",
        required=True,
    )
    category_type = fields.Many2many(
        "product.public.category", string="Category"
    )
    redemption_customer = fields.Integer(
        string="Redemption Customer", required=True
    )
    discount_type = fields.Selection(
        [("fixed", "Fixed"), ("percentage", "Percentage")],
        default="fixed",
        string="Discount Type",
        required=True,
    )
    discount = fields.Float(string="Discount", required=True)
    minimum_qty = fields.Float(string="Minimum Qty")
    minimum_amount = fields.Float(string="Minimum Amount")
    redeem_voucher_ids = fields.One2many(
        comodel_name="redeem.voucher",
        inverse_name="voucher_name",
        string="Redeem Voucher",
    )
    voucher_image = fields.Binary(string="Image")
    description = fields.Text(string="Description")

    @api.model
    def create(self, vals):
        voucher_id = self.search(
            [("code", "=", vals["code"])], limit=5, order="id desc"
        )
        for voucher_id_detail in voucher_id:
            for voucher_detail in voucher_id_detail:
                if voucher_detail.expiry_date >= date.today():
                    raise Warning(_("Voucher already exist"))
        if not vals["code"]:
            vals["code"] = "".join(
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                for i in range(7)
            )
        return super(GiftVoucher, self).create(vals)

    @api.constrains(
        "expiry_date",
        "minimum_amount",
        "discount",
        "redemption_customer",
        "voucher_type",
    )
    def check_unique_date(self):
        now = datetime.now().date()
        if not self.expiry_date > now:
            raise ValidationError("Date must be greter then today date")

        if (
            self.voucher_type == "order_total"
            and not self.minimum_amount > 0
        ):
            raise ValidationError(
                "Please enter minimum valid voucher amount must be greter then zero"
            )

        if self.discount_type == "percentage":
            if self.discount <= 0 or self.discount > 100:
                raise ValidationError(
                    _("Percentage must be between 0 to 100")
                )

        elif self.discount_type == "fixed" and not self.discount > 0:
            raise ValidationError(
                "Please enter valid discount must be greter then zero"
            )

        if not self.redemption_customer > 0:
            raise ValidationError(
                "Please enter minimum redemption customer must be greter then zero"
            )


class RedeemVoucher(models.Model):
    _name = "redeem.voucher"
    _description = "Redeem Voucher Info"

    voucher_name = fields.Many2one(
        "gift.voucher.detail", string="Voucher Name"
    )
    voucher_code = fields.Char(string="Code")
    order_name = fields.Char(string="Order")
    order_amount = fields.Float(string="Order Amount")
    voucher_amount = fields.Float(string="Voucher Amount")
    used_date = fields.Date(
        string="Used Date", default=fields.Datetime.now(), store=True
    )
    customer_id = fields.Many2one("res.partner", string="Customer")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
