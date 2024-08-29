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
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo.api import Environment
from odoo.http import request
from odoo.tools import lazy_property


# class CompanyBranch(models.Model):
#     _name = 'company.branch'
#     _description = 'Company Branch'
#
#     name = fields.Char(string="Branch Name", required=True)
#     company_id = fields.Many2one('res.company', string="Company", required=True)
#     phone = fields.Char(string="Phone")
#     street = fields.Char()
#     street2 = fields.Char()
#     zip = fields.Char(change_default=True)
#     city = fields.Char()
#     state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
#     country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
#     parent_id = fields.Many2one('company.branch', string="Parent Branch")
#     email_id = fields.Char(string="Email")
#
#     @api.constrains('parent_id')
#     def _check_parent_id(self):
#         if not self._check_recursion():
#             raise ValidationError(_('Error ! You cannot create recursive Branch.'))
#
#     @api.model
#     def get_allowed_branch_data(self):
#         """
#         :return:
#         """
#         bids_lst = []
#         if request.httprequest.cookies.get('bids'):
#             for branch in request.httprequest.cookies.get('bids'):
#                 if branch.isnumeric():
#                     branch_id = request.env['company.branch'].sudo().browse(
#                         int(branch))
#                     if branch_id.exists():
#                         bids_lst.append(int(branch))
#         if len(bids_lst) == 1:
#             bids_tpl = bids_lst[0]
#             bids_lst = self.search_read([('id', '=', bids_tpl)])
#         else:
#             bids_tpl = tuple(bids_lst)
#             bids_lst = self.search_read([('id', 'in', bids_tpl)])
#         return bids_lst


# # Environment changes
# @lazy_property
# def branch(self):
#     branch_ids = self.context.get('allowed_branch_ids', [])
#     print('\n\n--->branch_ids----->1', branch_ids)
#     if branch_ids:
#         if isinstance(branch_ids[0], list):
#             branch_ids = branch_ids[0]
#         if not self.su:
#             user_branch_ids = self.user.branch_ids.ids
#             if type(branch_ids[0]) == 'list':
#                 if any(bid not in user_branch_ids for bid in branch_ids[0]):
#                     raise AccessError(_("Access to unauthorized or invalid branches11111111."))
#         return self['company.branch'].browse(branch_ids[0])
#     return self.user.branch_id.with_env(self)
#
#
# @lazy_property
# def branches(self):
#     branch_ids = self.context.get('allowed_branch_ids', [])
#     print('\n\n--->branch_ids----->2', branch_ids)
#     if branch_ids:
#         if isinstance(branch_ids[0], list):
#             branch_ids = branch_ids[0]
#         if not self.su:
#             user_branch_ids = self.user.branch_ids.ids
#             if type(branch_ids[0]) == 'list':
#                 if any(bid not in user_branch_ids for bid in branch_ids):
#                     raise AccessError(_("Access to unauthorized or invalid branches."))
#         return self['company.branch'].browse(branch_ids)
#     return self.user.branch_ids.with_env(self)
#
#
# ev = Environment
# ev.branch_id = branch
# ev.branch_ids = branches
#
#
# class ResUsers(models.Model):
#     _inherit = 'res.users'
#
#     def get_current_branch(self):
#         """
#         :return:
#         """
#         print('\n\n---->>>>env.context', self.env.context)
#         allow_branch = \
#             self.env.company and self.env.company.branch_ids.ids or []
#         current_branch = self.env.branch_id and self.env.branch_id.id or False
#         if not current_branch:
#             current_branch = self.current_branch_id.id
#         if current_branch and allow_branch:
#             if current_branch in allow_branch:
#                 return current_branch
#         return False
#
#     def write(self, vals):
#         self = self.sudo()
#         res = super(ResUsers, self).write(vals)
#         if vals.get('company_id') and not vals.get('branch_id'):
#             company_id = self.env['res.company'].browse(vals.get('company_id'))
#             if company_id.branch_ids:
#                 for user in self:
#                     user.write(
#                         {'branch_ids': [(6, 0, company_id.branch_ids.ids)],
#                          'branch_id': company_id.branch_ids.ids[0]})
#             else:
#                 raise ValidationError(
#                     _('There is no branch for company %s.' % company_id.name))
#         self.env.registry.clear_cache()
#         return res
#
#     # @api.constrains('branch_id', 'branch_ids')
#     # def _check_company_branch(self):
#     #     if any(
#     #     user.branch_ids and user.branch_id not in user.branch_ids for user
#     #     in self):
#     #         raise ValidationError(
#     #             _('The chosen branch is not in the allowed branches for '
#     #               'this user'))
#
#     @api.onchange('company_ids')
#     def onchange_allow_companies(self):
#         if self.company_ids:
#             branch_ids = self.company_ids.mapped('branch_ids')
#             self.branch_ids = [(6, 0, branch_ids.ids if branch_ids else [])]
#
#     @api.onchange('company_id')
#     def onchange_company_id(self):
#         if self.company_id and not self.company_ids:
#             branch_ids = self.company_id.branch_ids
#             self.branch_id = branch_ids[0].id
#             self.branch_ids = branch_ids.ids
#
#     @api.model
#     def _company_branch_unit(self):
#         if self.env.user.branch_id:
#             return self.env.user.branch_id
#         else:
#             # main_branch = self.env.ref('aspl_branch_pos_kitchen_screen.main_branch')
#             return False
#
#     @api.model
#     def _company_branch_units(self):
#         return self._company_branch_unit()
#
#     branch_id = fields.Many2one(
#         'company.branch', string="Current Branch")
#     branch_ids = fields.Many2many(
#         'company.branch', 'company_branch_users_rel', 'user_id',
#         'branch_id', string="Allowed Branches")
#
#     current_branch_ids = fields.Many2many(
#         'company.branch', 'rel_tbl_branch_user', 'uid', 'bid',
#         'Current Branches', default=lambda self: self._company_branch_units())
#     current_branch_id = fields.Many2one(
#         'company.branch', 'Current Branch',
#         default=lambda self: self._company_branch_unit())
#
#
# class IrRule(models.Model):
#     _inherit = 'ir.rule'
#
#     @api.model
#     def _eval_context(self):
#         """Returns a dictionary to use as evaluation context for
#            ir.rule domains.
#            Note: company_ids contains the ids of the activated companies
#            by the user with the switch company menu. These companies are
#            filtered and trusted.
#         """
#         res = super(IrRule, self)._eval_context()
#         res.update({'branch_ids': self.env.branch_ids.sudo().ids})
#         return res
#
#
# class IrHttp(models.AbstractModel):
#     _inherit = 'ir.http'
#
#     def session_info(self):
#         user = request.env.user
#         display_switch_branch_menu = user.has_group(
#             'aspl_hotel.group_multi_branches') and len(
#             user.sudo().branch_ids.ids) > 1
#         result = super(IrHttp, self).session_info()
#
#         if request.httprequest.cookies.get('cids'):
#             allowed_companies = [
#                 int(company) for company in request.httprequest.cookies.get(
#                     'cids')
#                 if company.isnumeric()]
#         else:
#             allowed_companies = user.company_id.ids
#         current_branch_id = False
#         if request.httprequest.cookies.get('bids'):
#             bids_lst = []
#             company_set = set()
#             current_branch_id = request.httprequest.cookies.get('bids')[0]
#             for branch in request.httprequest.cookies.get('bids'):
#                 if branch.isnumeric():
#                     branch_id = request.env[
#                         'company.branch'].sudo().browse(int(branch))
#                     if branch_id.exists():
#                         bids_lst.append(int(branch))
#                         company_set.add(int(branch_id.company_id.id))
#             if len(bids_lst) <= 1 and user.sudo().branch_id.id not in bids_lst:
#                 bids_lst.append(user.sudo().branch_id.id)
#             new_company_ids = list(set(allowed_companies) - company_set)
#             if new_company_ids:
#                 company_ids = request.env[
#                     'res.company'].sudo().browse(new_company_ids)
#                 if company_ids.exists():
#                     bids_lst.extend(user.sudo().branch_ids.filtered(
#                         lambda branch: branch.company_id.id in company_ids.ids
#                     ).ids)
#             allowed_branches = self.env[
#                 'company.branch'].sudo().browse(bids_lst).filtered(
#                 lambda x: x.company_id.id in allowed_companies).ids
#             if request.httprequest.cookies.get('cids'):
#                 allowed_branches = self.env['company.branch'].sudo().search([
#                     ('company_id', 'in', allowed_companies)]).ids
#         else:
#             allowed_branches = user.sudo().branch_ids.ids
#             current_branch_id = allowed_branches and allowed_branches[0]
#         allowed_branches = list(set(allowed_branches).intersection(user.sudo().branch_ids.ids))
#         print('\n\n--->>>allowed_branches', allowed_branches)
#         if allowed_branches:
#             user.write({
#                 'current_branch_ids': [
#                     (3, each.id) for each in user.current_branch_ids],
#
#                 # 'branch_ids': [(3, each.id) for each in user.branch_ids]
#             })
#             user.write({
#                 'current_branch_ids': [(4, each) for each in allowed_branches],
#                 # 'branch_ids': [(4, each.id) for each in self.env[
#                 #     'res.company'].browse(allowed_companies).mapped('branch_ids')
#                 #                if each.company_id.id in user.company_ids.ids]
#             })
#             result.update({
#                 'display_switch_branch_menu': user.has_group(
#                     'aspl_hotel.group_multi_branches') and len(
#                     user.sudo().branch_ids) > 1,
#                 'branch_id': user.sudo().branch_id.id if request.session.uid
#                 else None,
#                 'user_branches': {
#                     'current_branch': user.sudo().current_branch_ids and [
#                         user.sudo().current_branch_ids[0].id] or [],
#                     'allowed_branches': {
#                         branch.id: {
#                             'id': branch.id,
#                             'name': branch.name,
#                             'company_id': branch.company_id.id,
#                         } for branch in user.sudo().current_branch_ids
#                     },
#                     'currentBranch': {
#                         'id': user.sudo().branch_ids and user.sudo().branch_ids[
#                             0].id or False,
#                         'name': user.sudo().branch_ids and user.sudo(
#                         ).branch_ids[0].name
#                     }}
#                 if display_switch_branch_menu else False,
#             })
#             result.get('user_context').update({
#                 'allowed_branch_ids': allowed_branches
#             })
#         print('\n\n---->>>>result', result)
#         return result


# class IrHttp(models.AbstractModel):
#     _inherit = 'ir.http'
#
#     def session_info(self):
#         user = request.env.user
#         display_switch_branch_menu = user.has_group(
#             'aspl_hotel.group_multi_branches') and len(
#             user.sudo().branch_ids.ids) > 1
#         result = super(IrHttp, self).session_info()
#
#         if request.httprequest.cookies.get('cids'):
#             allowed_companies = [
#                 int(company) for company in request.httprequest.cookies.get(
#                     'cids')
#                 if company.isnumeric()]
#         else:
#             allowed_companies = user.company_id.ids
#         current_branch_id = False
#         if request.httprequest.cookies.get('bids'):
#             bids_lst = []
#             company_set = set()
#             current_branch_id = request.httprequest.cookies.get('bids')[0]
#             for branch in request.httprequest.cookies.get('bids'):
#                 if branch.isnumeric():
#                     branch_id = request.env[
#                         'company.branch'].sudo().browse(int(branch))
#                     if branch_id.exists():
#                         bids_lst.append(int(branch))
#                         company_set.add(int(branch_id.company_id.id))
#             if len(bids_lst) <= 1 and user.sudo().branch_id.id not in bids_lst:
#                 bids_lst.append(user.sudo().branch_id.id)
#             new_company_ids = list(set(allowed_companies) - company_set)
#             if new_company_ids:
#                 company_ids = request.env[
#                     'res.company'].sudo().browse(new_company_ids)
#                 if company_ids.exists():
#                     bids_lst.extend(user.sudo().branch_ids.filtered(
#                         lambda branch: branch.company_id.id in company_ids.ids
#                     ).ids)
#             allowed_branches = self.env[
#                 'company.branch'].sudo().browse(bids_lst).filtered(
#                 lambda x: x.company_id.id in allowed_companies).ids
#             if request.httprequest.cookies.get('cids'):
#                 allowed_branches = self.env['company.branch'].sudo().search([
#                     ('company_id', 'in', allowed_companies)]).ids
#         else:
#             allowed_branches = user.sudo().branch_ids.ids
#             current_branch_id = allowed_branches and allowed_branches[0]
#         if allowed_branches:
#             user.write({
#                 'current_branch_ids': [
#                     (3, each.id) for each in user.current_branch_ids],
#                 # 'branch_ids': [(3, each.id) for each in user.branch_ids]
#             })
#             user.write({
#                 'current_branch_ids': [(4, each) for each in allowed_branches],
#                 # 'branch_ids': [(4, each.id) for each in self.env[
#                 #     'res.company'].browse(allowed_companies).mapped('branch_ids')
#                 #                if each.company_id.id in user.company_ids.ids]
#             })
#
#             result.update({
#                 'display_switch_branch_menu': user.has_group(
#                     'aspl_hotel.group_multi_branches') and len(
#                     user.sudo().branch_ids) > 1,
#                 'branch_id': user.sudo().branch_id.id if request.session.uid
#                 else None,
#                 # 'user_companies': {
#                 #     'current_company': [2],
#                 #     'allowed_companies': {1: {'id': 1, 'name': "abc", }, 2 : {'id': 2, 'name': 'Vishal'}},
#                 #     'currentCompany': {
#                 #         'id': 2,
#                 #         'name': 'Vishal'
#                 #     }
#                 # },
#                 'user_branches': {
#                     'current_branch': user.sudo().current_branch_ids and [
#                         user.sudo().current_branch_ids[0].id] or [],
#                     'allowed_branches': {
#                         branch.id: {
#                             'id': branch.id,
#                             'name': branch.name,
#                         } for branch in user.sudo().current_branch_ids
#                     },
#                     'currentBranch': {
#                         'id': user.sudo().branch_ids and user.sudo().branch_ids[
#                             0].id or False,
#                         'name': user.sudo().branch_ids and user.sudo(
#                         ).branch_ids[0].name
#                     }}
#                 if display_switch_branch_menu else False,
#             })
#             result.get('user_context').update({
#                 'allowed_branch_ids': allowed_branches,
#                 # 'allowed_company_ids': [1,2]
#             })
#         return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
