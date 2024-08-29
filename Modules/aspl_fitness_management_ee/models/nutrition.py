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


class FoodItem(models.Model):
    _name = 'food.item'
    _description = 'Food Item'

    name = fields.Char("Name")
    description = fields.Char("Description")
    group_id = fields.Many2one('food.group', string="Food Group")
    image = fields.Binary("Image")
    nutrients_value_ids = fields.One2many('food.nutrients.value', 'item_id',
                                          string="Food Nutrients")


class FoodGroup(models.Model):
    _name = 'food.group'
    _description = 'Food Group'

    name = fields.Char("Name")
    description = fields.Char("Description")
    food_item_id = fields.One2many('food.item', 'group_id', string="Food Item")


class FoodNutrients(models.Model):
    _name = 'food.nutrients'
    _description = 'Food Nutrients'

    name = fields.Char("Name")
    description = fields.Char("Description")
    uom_id = fields.Many2one('uom.uom', string="Unit")


class MealNutrients(models.Model):
    _name = 'nutrition.meal'
    _description = 'Nutrition Meal'

    name = fields.Char("Name")
    order = fields.Integer("Order")
    meal_line_ids = fields.One2many('meal.lines', 'meal_id', string="Meal")
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    meal_time = fields.Float("Meal Time")
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.company)
    branch_id = fields.Many2one('company.branch', string="Branch")


class MealLine(models.Model):
    _name = 'meal.lines'
    _description = 'Meal Time'
    _rec_name = 'meal_id'

    meal_id = fields.Many2one('nutrition.meal', string="Meal")
    food_item_id = fields.Many2one('food.item', string="Food")
    description = fields.Char("Description")
    uom_id = fields.Many2one('uom.uom', string="Unit")
    qty = fields.Float("Qty")


class FoodNutritionValue(models.Model):
    _name = 'food.nutrients.value'
    _description = 'Nutrients Value'
    _rec_name = 'nutrients_id'

    item_id = fields.Many2one('food.item', string="Food")
    nutrients_id = fields.Many2one('food.nutrients', string="Nutrient")
    uom_id = fields.Many2one('uom.uom', string="Unit")
    qty = fields.Float("Qty")

    @api.onchange('nutrients_id')
    def onchange_nutrients_id(self):
        """
        :return:
        """
        if self.nutrients_id and self.nutrients_id.uom_id:
            self.uom_id = self.nutrients_id.uom_id.id


class NutritionPlanLines(models.Model):
    _name = 'nutrition.plan.lines'
    _description = 'Nutrition Plan Lines'
    _rec_name = 'plan_id'

    day = fields.Selection([('1', 'Monday'),
                            ('2', 'Tuesday'),
                            ('3', 'Wednesday'),
                            ('4', 'Thursday'),
                            ('5', 'Friday'),
                            ('6', 'Saturday'),
                            ('7', 'Sunday')], string="Day", default="1")
    meal_ids = fields.Many2many('nutrition.meal', 'nutrition_meal_plan_lines_rel',
                                'nutrition_plan_lines_id',
                                'nutrition_meal_id', string="Meals")
    plan_id = fields.Many2one('subscriber.plan', string="Subscriber Plan")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
