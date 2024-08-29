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


class SalesPersonConfiguration(models.TransientModel):
    _description = 'Sale Person Configuration'
    _name = 'sales.person.configuration'

    sales_person_all = fields.Boolean(string='All Sales Person')
    sales_person_job_ids = fields.Many2many('hr.job', 'sales_job_rel', string="Job Position(s)")
    sales_person_ids = fields.Many2many('res.users', string="User(s)")
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
    user_ids = fields.Many2many('res.partner', 'par_rel', string="Customer(s)")
    team_ids = fields.Many2many('crm.team', string="Sale Team(s)")
    product_compute_price_type = fields.Selection([('fix_price', 'Fix Price'),
                                                   ('per', 'Percentage')],
                                                  string="Product Compute Price", default="per")
    product_commission = fields.Float(string="Product Commission")
    product_categ_compute_price_type = fields.Selection([('fix_price', 'Fix Price'),
                                                         ('per', 'Percentage')],
                                                        string="Product Category Compute Price",
                                                        default="per")
    product_categ_commission = fields.Float(string="Product Category Commission")
    customer_compute_price_type = fields.Selection([('fix_price', 'Fix Price'),
                                                    ('per', 'Percentage')],
                                                   string="Customer Compute Price", default="per")
    customer_commission = fields.Float(string="Customer Commission")
    team_compute_price_type = fields.Selection([('fix_price', 'Fix Price'), ('per', 'Percentage')],
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

    def job_related_users(self, jobid):
        if jobid:
            empids = self.env['hr.employee'].search([('user_id', '!=', False),
                                                     ('job_id', '=', jobid.id)])
            return [emp.user_id.id for emp in empids]
        return False

    def apply_config(self):
        job_ids = self.sales_person_job_ids if not self.sales_person_all \
            else self.env['hr.job'].search([])
        user_ids = self.sales_person_ids if not self.sales_person_all \
            else self.env['res.users'].search([])
        product_ids = self.product_ids if not self.all_products \
            else self.env['product.product'].search([])
        category_ids = self.category_ids if not self.all_categories \
            else self.env['product.category'].search([])
        usr_ids = self.user_ids if not self.all_customers \
            else self.env['res.partner'].search([])
        team_ids = self.team_ids if not self.all_sales_teams \
            else self.env['crm.team'].search([])
        if job_ids or user_ids:
            vals = {}
            # users = self.env['res.users'].browse(user_ids)
            # print('#########users#',users)
            for job in job_ids:
                vals[job] = self.env['res.users']
                emp_user_lst = self.job_related_users(job)
                for user in user_ids:
                    print('##########',user.id)
                    print('##########',emp_user_lst)
                    if user.id in emp_user_lst:
                        vals[job] += user
                        # user_ids.ids -= user.id
                        user_ids.ids.remove(user.id)

            vals = {user: [] for user in user_ids}
            for key, value in vals.items():
                if self.to_product:
                    for product in product_ids:
                        comm_vals = {
                            'job_id': key.id,
                            'compute_price_type': self.product_compute_price_type,
                            'commission': self.product_commission
                        }
                        if key._name == 'hr.job':
                            comm_vals.update({
                                'job_id': key.id,
                                'user_ids': [(6, 0, [x.id for x in value])]
                            })
                        elif key._name == 'res.users':
                            comm_vals.update({
                                'job_id': False,
                                'user_ids': [(6, 0, [key.id])]
                            })
                        product.write({'product_comm_ids': [(0, 0, comm_vals)]})
                if self.to_product_categ:
                    for category in category_ids:
                        comm_vals = {
                            'compute_price_type': self.product_categ_compute_price_type,
                            'commission': self.product_categ_commission
                        }
                        for key, value in vals.items():
                            if key._name == 'hr.job':
                                comm_vals.update({
                                    'job_id': key.id,
                                    'user_ids': [(6, 0, [x.id for x in value])]
                                })
                            elif key._name == 'res.users':
                                comm_vals.update({
                                    'job_id': False,
                                    'user_ids': [(6, 0, [key.id])]
                                })
                        category.write({'prod_categ_comm_ids': [(0, 0, comm_vals)]})
                if self.to_sales_team:
                    for team in team_ids:
                        comm_vals = {
                            'compute_price_type': self.team_compute_price_type,
                            'commission': self.team_commission
                        }
                        if key._name == 'hr.job':
                            comm_vals.update({
                                'job_id': key.id,
                                'user_ids': [(6, 0, [x.id for x in value])]
                            })
                        elif key._name == 'res.users':
                            comm_vals.update({
                                'job_id': False,
                                'user_ids': [(6, 0, [key.id])]
                            })
                        team.write({'sale_team_comm_ids': [(0, 0, comm_vals)]})
                if self.to_customer:
                    for customer in usr_ids:
                        comm_vals = {
                            'job_id': key.id,
                            'compute_price_type': self.customer_compute_price_type,
                            'commission': self.customer_commission
                        }
                        if key._name == 'hr.job':
                            comm_vals.update({
                                'job_id': key.id,
                                'user_ids': [(6, 0, [x.id for x in value])]
                            })
                        elif key._name == 'res.users':
                            comm_vals.update({
                                'job_id': False,
                                'user_ids': [(6, 0, [key.id])]
                            })
                        customer.write({'comm_ids': [(0, 0, comm_vals)]})
        else:
            raise UserError(_('Please select Sales Person to '
                              'generate commission calculation data.'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
