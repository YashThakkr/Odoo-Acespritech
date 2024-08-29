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

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GymPlan(models.Model):
    _name = 'gym.plan'
    _description = 'Gym Plan'

    name = fields.Char("Name")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    plan_line_ids = fields.One2many('gym.plan.line', 'plan_id', string="Plan")

    @api.depends('plan_line_ids', 'plan_line_ids.fees')
    def _compute_total_fees(self):
        for each_plan in self:
            total_fees = 0
            for each in each_plan.plan_line_ids:
                total_fees += each.fees
            each_plan.total_fees = total_fees

    total_fees = fields.Float("Total", compute="_compute_total_fees", store=True)
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 default=lambda self: self.env.company)
    branch_ids = fields.Many2many('company.branch', 'rel_gym_plan_branch', 'plan_id', 'branch_id',
                                  string="Branches")

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.start_date > self.end_date:
            raise ValidationError('End date must be greater than start date')


class GymPlanLines(models.Model):
    _name = 'gym.plan.line'
    _description = 'Gym Plan Lines'
    _rec_name = 'service_id'

    desc = fields.Char("Description")
    fees = fields.Float("Fees")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain=[('is_gym_service', '=', True)])
    plan_id = fields.Many2one('gym.plan', string="Plan")

    @api.onchange('service_id')
    def _onchange_service_id(self):
        for each in self:
            service_product_id = self.env['product.product'].search(
                [('name', '=', each.service_id.name)])
            if service_product_id:
                each.desc = service_product_id.name
                each.fees = service_product_id.list_price


class GymExercise(models.Model):
    _name = 'gym.exercise'
    _description = 'Gym Exercise'

    name = fields.Char("Name")
    description = fields.Char("Description")
    image = fields.Binary(string="Image")
    equipment_ids = fields.Many2many('product.product', 'exercise_equipment_rel',
                                     'exercise_id', 'equipment_id', string="Equipments")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain=[('is_gym_service', '=', True)])
    attachment_ids = fields.Many2many('ir.attachment', 'attachment_exercise_plan_rel',
                                      'exercise_id', 'attachment_id',
                                      string="Attachment")
    service_tmpl_id = fields.Many2one('product.template', string="Product")


class GymServiceLine(models.Model):
    _name = 'gym.service.line'
    _description = 'Gym Service Lines'
    _rec_name = 'service_id'

    service_id = fields.Many2one('product.product', string="Service",
                                 domain=[('is_gym_service', '=', True)])
    fees = fields.Float("Fees")
    description = fields.Char("Description")
    with_trainer = fields.Boolean("With Trainer")
    subscriber_plan_id = fields.Many2one('subscriber.plan', string="Subscriber Plan",
                                         ondelete="cascade")
    pricelist_id = fields.Many2one('product.pricelist', string="pricelist")

    @api.onchange('service_id')
    def _onchange_service(self):
        if self.service_id:
            self.description = self.service_id.description
            self.fees = self._get_display_price(self.service_id)

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        price_list_item = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = price_list_item.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and \
                        pricelist_item.base_pricelist_id and \
                        pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(
                        uom=uom.id).get_product_price_rule(product, qty,
                                                           self.subscriber_plan_id.subscriber_id)
                    pricelist_item = price_list_item.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
                product_currency = product.cost_currency_id
            elif pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(
                    product_currency, currency_id,
                    self.subscriber_plan_id.company_id or self.env.company,
                    self.subscriber_plan_id.create_date or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    def _get_display_price(self, product):
        if self.subscriber_plan_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.subscriber_plan_id.pricelist_id.id,
                                        uom=self.service_id.uom_id.id).price
        product_context = dict(self.env.context,
                               partner_id=self.subscriber_plan_id.subscriber_id.id,
                               date=self.subscriber_plan_id.create_date,
                               uom=self.service_id.uom_id.id)

        final_price, rule_id = self.subscriber_plan_id.pricelist_id.with_context(
            product_context).get_product_price_rule(
            product or self.service_id, 1.0, self.subscriber_plan_id.subscriber_id)
        base_price, currency = self.with_context(
            product_context)._get_real_price_currency(
            product, rule_id, 1, self.service_id.uom_id,
            self.subscriber_plan_id.pricelist_id.id)
        if currency != self.subscriber_plan_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.subscriber_plan_id.pricelist_id.currency_id,
                self.subscriber_plan_id.company_id or self.env.company,
                self.subscriber_plan_id.create_date or fields.Date.today())
        return base_price

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
