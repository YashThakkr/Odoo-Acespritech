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

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ConsultantConfiguration(models.TransientModel):
    _description = 'Consultant Configuration'
    _name = 'consultant.configuration'

    consultant_all = fields.Boolean(string='All Consultants')
    consultant_ids = fields.Many2many('res.partner', 'consultant_rel', string="Consultants(s)")
    to_customer = fields.Boolean(string='Customer')
    to_product = fields.Boolean(string='Product')
    to_product_categ = fields.Boolean(string='Product Category')
    to_sales_team = fields.Boolean(string='Sales Team')
    all_customers = fields.Boolean(string='All Customers')
    all_products = fields.Boolean(string='All Products')
    all_categories = fields.Boolean(string='All Categories')
    all_sales_teams = fields.Boolean(string='All Sales Teams')
    product_ids = fields.Many2many('product.product', string="Product(s)")
    category_ids = fields.Many2many('product.category', string="Product Category(s)")
    partner_ids = fields.Many2many('res.partner', 'rel', string="Customer(s)")
    team_ids = fields.Many2many('crm.team', string="Sale Team(s)")
    product_compute_price_type = fields.Selection(
        [('fix_price', 'Fix Price'),
         ('per', 'Percentage')],
        string="Product Compute Price", default="per")
    product_commission = fields.Float(string="Product Commission")
    product_categ_compute_price_type = fields.Selection(
        [('fix_price', 'Fix Price'),
         ('per', 'Percentage')],
        string="Product Category Compute Price", default="per")
    product_categ_commission = fields.Float(string="Product Category Commission")
    customer_compute_price_type = fields.Selection(
        [('fix_price', 'Fix Price'),
         ('per', 'Percentage')],
        string="Customer Compute Price", default="per")
    customer_commission = fields.Float(string="Customer Commission")
    team_compute_price_type = fields.Selection([('fix_price', 'Fix Price'),
                                                ('per', 'Percentage')],
                                               string="Sales Team Compute Price", default="per")
    team_commission = fields.Float(string="Sales Team Commission")

    @api.constrains('product_commission', 'product_compute_price_type',
                    'product_categ_commission', 'product_categ_compute_price_type',
                    'customer_commission', 'customer_compute_price_type',
                    'team_commission', 'team_compute_price_type')
    def check_commissions(self):
        for record in self:
            if record.product_commission and record.product_compute_price_type == 'per' and (
                    record.product_commission < 0.0 or record.product_commission > 100):
                raise UserError(_('Commission value for Percentage type must be between 0 to 100.'))
            if record.product_categ_commission and record.product_categ_compute_price_type == 'per' and (
                    record.product_categ_commission < 0.0 or record.product_categ_commission > 100):
                raise UserError(_('Commission value for Percentage type must be between 0 to 100.'))
            if record.customer_commission and record.customer_compute_price_type == 'per' and (
                    record.customer_commission < 0.0 or record.customer_commission > 100):
                raise UserError(_('Commission value for Percentage type must be between 0 to 100.'))
            if record.team_commission and record.team_compute_price_type == 'per' and (
                    record.team_commission < 0.0 or record.team_commission > 100):
                raise UserError(_('Commission value for Percentage type must be between 0 to 100.'))
    def apply_config(self):
        cons_ids = self.consultant_ids if not self.consultant_all else \
            self.env['res.partner'].search([('is_consultant', '=', True)])
        product_ids = self.product_ids if not self.all_products else \
            self.env['product.product'].search([])
        category_ids = self.category_ids if not self.all_categories else \
            self.env['product.category'].search([])
        partner_ids = self.partner_ids if not self.all_customers else \
            self.env['res.partner'].search([])
        team_ids = self.team_ids if not self.all_sales_teams else \
            self.env['crm.team'].search([])
        if cons_ids:
            if self.to_product:
                for product in product_ids:
                    product_cons_comm_ids = [(0, 0, {'partner_id': consultant.id,
                                                     'compute_price_type': self.product_compute_price_type,
                                                     'commission': self.product_commission})
                                             for consultant in cons_ids]
                    product.write({'product_cons_comm_ids': product_cons_comm_ids})
            if self.to_product_categ:
                for category in category_ids:
                    prod_categ_cons_comm_ids = [(0, 0, {'partner_id': consultant.id,
                                                           'compute_price_type': self.product_categ_compute_price_type,
                                                           'commission': self.product_categ_commission})
                                                   for consultant in cons_ids]
                    category.write({'prod_categ_cons_comm_ids': prod_categ_cons_comm_ids})
            if self.to_sales_team:
                for team in team_ids:
                    sale_team_cons_comm_ids = [(0, 0, {'partner_id': consultant.id,
                                                       'compute_price_type': self.team_compute_price_type,
                                                       'commission': self.team_commission})
                                               for consultant in cons_ids]
                    team.write({'sale_team_cons_comm_ids': sale_team_cons_comm_ids})
            if self.to_customer:
                for customer in partner_ids:
                    consultant_comm_ids = [(0, 0, {'partner_id': consultant.id,
                                                   'compute_price_type': self.customer_compute_price_type,
                                                   'commission': self.customer_commission})
                                           for consultant in cons_ids if consultant.id != customer.id]
                    customer.write({'consultant_comm_ids': consultant_comm_ids})
        else:
            raise UserError(_('Please select Consultants to generate commission calculation data.'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
