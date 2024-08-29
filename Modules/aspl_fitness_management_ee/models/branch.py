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

import math

from odoo import models, fields, api, _
from odoo.api import Environment
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request
from odoo.tools import lazy_property
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.base.models.ir_module import assert_log_admin_access



@lazy_property
def branch(self):
    branch_ids = self.context.get('allowed_branch_ids', [])
    if branch_ids:
        if isinstance(branch_ids[0], list):
            branch_ids = branch_ids[0]
        if not self.su:
            user_branch_ids = self.user.branch_ids.ids
            if type(branch_ids[0]) == 'list':
                if any(bid not in user_branch_ids for bid in branch_ids[0]):
                    raise AccessError(_("Access to unauthorized or invalid branches11111111."))
        return self['company.branch'].browse(branch_ids[0])
    return self.user.branch_id.with_env(self)


@lazy_property
def branches(self):
    branch_ids = self.context.get('allowed_branch_ids', [])
    if branch_ids:
        if isinstance(branch_ids[0], list):
            branch_ids = branch_ids[0]
        if not self.su:
            user_branch_ids = self.user.branch_ids.ids
            if type(branch_ids[0]) == 'list':
                if any(bid not in user_branch_ids for bid in branch_ids):
                    raise AccessError(_("Access to unauthorized or invalid branches."))
        return self['company.branch'].browse(branch_ids)
    return self.user.branch_ids.with_env(self)


class CompanyBranch(models.Model):
    _name = 'company.branch'
    _description = "Company's Branch"

    name = fields.Char(string="Branch Name", required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 default=lambda self: self.env.company)
    phone = fields.Char(string="Phone")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip = fields.Char(change_default=True, string="Zip")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    parent_id = fields.Many2one('company.branch', string="Parent Branch")
    stock_location_id = fields.Many2one('stock.location', string="Stock Location")
    service_location_id = fields.Many2one('stock.location', string="Service Location")
    opening_hours = fields.Float("Opening Hours")
    closing_hours = fields.Float("Closing Hours")
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Hours')
    # branch_shift_ids = fields.One2many('branch.shift', 'branch_id', string="Branch")

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive Branch.'))

    @api.constrains('opening_hours', 'closing_hours')
    def _check_opening_closing_hours(self):
        for each in self:
            if each.opening_hours and each.closing_hours:
                if each.closing_hours < each.opening_hours:
                    raise ValidationError(
                        _('Closing Hours cannot be earlier than Opening Hours.'))
            elif each.opening_hours == 0 or each.closing_hours == 0:
                raise ValidationError(_('Please Mention Branch Opening and Closing Time.'))

    @api.model
    def get_allowed_branch_ids(self):
        bids_lst = []
        if request.httprequest.cookies.get('bids'):
            for branch in request.httprequest.cookies.get('bids'):
                if branch.isnumeric():
                    branch_id = request.env['company.branch'].sudo().browse(
                        int(branch))
                    if branch_id.exists():
                        bids_lst.append(int(branch))
        return bids_lst

    @api.model
    def get_allowed_branch_data(self):
        """
        :return:
        """
        bids_lst = []
        if request.httprequest.cookies.get('bids'):
            for branch in request.httprequest.cookies.get('bids'):
                if branch.isnumeric():
                    branch_id = request.env['company.branch'].sudo().browse(
                        int(branch))
                    if branch_id.exists():
                        bids_lst.append(int(branch))
        if len(bids_lst) == 1:
            bids_tpl = bids_lst[0]
            bids_lst = self.search_read([('id', '=', bids_tpl)])
        else:
            bids_tpl = tuple(bids_lst)
            bids_lst = self.search_read([('id', 'in', bids_tpl)])
        return bids_lst


class ResUsers(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        self = self.sudo()
        res = super(ResUsers, self).write(vals)
        if vals.get('company_id') and not vals.get('branch_id'):
            company_id = self.env['res.company'].browse(vals.get('company_id'))
            if company_id.branch_ids:
                for user in self:
                    user.write({'branch_ids': [(6, 0, company_id.branch_ids.ids)],
                                'branch_id': company_id.branch_ids.ids[0]})
            else:
                raise ValidationError(_('There is no branch for company %s.' % company_id.name))
        self.env['ir.default'].clear_caches()
        return res

    # @api.constrains('branch_id', 'branch_ids')
    # def _check_company_branch(self):
    #     if any(user.branch_ids and user.branch_id not in user.branch_ids for user in self):
    #         raise ValidationError(
    #             _('The chosen branch is not in the allowed branches for this user'))

    @api.onchange('company_ids')
    def onchange_allow_companies(self):
        if self.company_ids:
            branch_ids = self.company_ids.mapped('branch_ids')
            self.branch_ids = [(6, 0, branch_ids.ids if branch_ids else [])]

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id and not self.company_ids:
            branch_ids = self.company_id.branch_ids
            self.branch_id = branch_ids[0].id
            self.branch_ids = branch_ids.ids
    @api.model
    def _company_branch_unit(self):
        if self.env.user.branch_id:
            return self.env.user.branch_id
        else:
            # main_branch = self.env.ref('aspl_fitness_management_ee.main_branch')
            return False

    @api.model
    def _company_branch_units(self):
        return self._company_branch_unit()

    branch_id = fields.Many2one(
        'company.branch', string="Current Branch")
    branch_ids = fields.Many2many(
        'company.branch', 'company_branch_users_rel', 'user_id',
        'branch_id', string="Allowed Branches")

    current_branch_ids = fields.Many2many(
        'company.branch', 'rel_tbl_branch_user', 'uid', 'bid',
        'Current Branches', default=lambda self: self._company_branch_units())
    current_branch_id = fields.Many2one(
        'company.branch', 'Current Branch',
        default=lambda self:self._company_branch_unit())

# class BranchShift(models.Model):
#     _name = "branch.shift"
#     _description = "Branch Shift"
#
#     opening_hours = fields.Float("Opening Hours")
#     closing_hours = fields.Float("Closing Hours")
#     branch_id = fields.Many2one('company.branch', string="Branch")
#     day = fields.Selection([('1', 'Monday'),
#                             ('2', 'Tuesday'),
#                             ('3', 'Wednesday'),
#                             ('4', 'Thursday'),
#                             ('5', 'Friday'),
#                             ('6', 'Saturday'),
#                             ('7', 'Sunday')], string="Day", default="1")
#
#     @api.constrains('opening_hours', 'closing_hours')
#     def _check_opening_closing_hours(self):
#         for each in self:
#             if each.opening_hours and each.closing_hours:
#                 if each.closing_hours < each.opening_hours:
#                     raise ValidationError(_('Closing hours cannot be earlier than opening hours.'))
#
#     @api.model
#     def create(self, vals):
#         res = super(BranchShift, self).create(vals)
#         for each in res:
#             if each.opening_hours <= 0:
#                 each.opening_hours = each.branch_id.opening_hours
#             if each.closing_hours <= 0:
#                 each.closing_hours = each.branch_id.closing_hours
#         return res
#
#     def write(self, vals):
#         res = super(BranchShift, self).write(vals)
#         for each in self:
#             if each.opening_hours <= 0:
#                 each.opening_hours = each.branch_id.opening_hours
#             if each.closing_hours <= 0:
#                 each.closing_hours = each.branch_id.closing_hours
#         return res


class BatchDuration(models.Model):
    _name = 'batch.duration'
    _description = 'Batch Duration'

    # Note: Default branch logic will change once multibranch widget is completed
    def _default_branch(self):
        active_user = self.env.user
        for company in active_user.company_ids:
            branch_ids = self.env['company.branch'].search([('company_id', '=', company.id)])
        return branch_ids

    name = fields.Char('Name')
    start_time = fields.Float("Start Time", default=7)
    start_time_meridiem = fields.Selection([('AM', 'AM'), ('PM', 'PM')], default='AM')
    end_time = fields.Float("End Time", default=7)
    end_time_meridiem = fields.Selection([('AM', 'AM'), ('PM', 'PM')], default='PM')
    interval = fields.Float("Interval")
    line_ids = fields.One2many('batch.duration.line', 'batch_id', string="Line")
    branch_id = fields.Many2one('company.branch', string="Branch", default=_default_branch)

    @api.constrains('start_time', 'end_time')
    def _check_start_end_time_validation(self):
        for rec in self:
            if rec.start_time and rec.start_time > 13.00:
                raise ValidationError(_('Selected Start Time is not Correct.'))
            if rec.end_time and rec.end_time > 13.00:
                raise ValidationError(_('Selected End Time is not Correct.'))

    def date_range(self, start_date, end_date, increment, period):
        result = []
        nxt = start_date
        delta = relativedelta(**{period: increment})
        while nxt <= end_date:
            result.append(nxt)
            nxt += delta
        return result

    def update_batch_slot(self):
        """
        Create Batch Slot
        :return:
        """
        if self.start_time and self.end_time and self.start_time_meridiem and self.end_time_meridiem and self.interval:
            self.line_ids.unlink()
            st = datetime.strftime(datetime.strptime(str(self.start_time).split('.')[0] + ':' + str(
                self.start_time).split('.')[1] + ' ' + self.start_time_meridiem, "%I:%M %p"), "%H:%M")
            et = datetime.strftime(datetime.strptime(str(self.end_time).split('.')[0] + ':' + str(
                self.end_time).split('.')[1] + ' ' + self.end_time_meridiem, "%I:%M %p"), "%H:%M")
            s_date = datetime.strptime('01-01-2021 ' + st, '%m-%d-%Y %H:%M')
            e_date = datetime.strptime('01-01-2021 ' + et, '%m-%d-%Y %H:%M')
            e_date = e_date - timedelta(hours=self.interval)
            date_range = self.date_range(s_date, e_date, self.interval, 'hours')
            slot_data = []
            for dr in date_range:
                slot_data.append([0, 0, {
                    'start_time': float(dr.strftime('%H.%M')),
                    'end_time': float((dr + timedelta(hours=self.interval)).strftime('%H.%M'))
                }])
            self.line_ids = slot_data
        else:
            self.line_ids.unlink()


class BatchDurationLine(models.Model):
    _name = 'batch.duration.line'
    _description = 'Batch Duration Line'
    _rec_name = 'batch_id'

    start_time = fields.Float("Start Time")
    end_time = fields.Float("End Time")
    batch_id = fields.Many2one('batch.duration', string="Batch")

    def name_get(self):
        super(BatchDurationLine, self).name_get()
        data = []
        for each in self:
            start_time = str("%02d" % int(math.modf(each.start_time)[1]) + ':' + "%02d" % int(
                round(60 * math.modf(each.start_time)[0], 2))) or ""
            end_time = str("%02d" % int(math.modf(each.end_time)[1]) + ':' + "%02d" % int(
                round(60 * math.modf(each.end_time)[0], 2))) or ""
            display_value = (each.batch_id.branch_id.name or "") + ' - (' + start_time + ' - ' + end_time + ')'
            data.append((each.id, display_value))
        return data

    # @api.model
    # def name_search(self, name='', args=None, operator='in', limit=80):
    #     branches = self.env['gym.plan'].browse(self._context.get('plan_id')).branch_ids
    #     batch_range_ids = self.search([('batch_id.branch_id', 'in', branches.ids)])
    #     return batch_range_ids.name_get()

# set branch and branches in environment

ev = Environment
ev.branch_id = branch
ev.branch_ids = branches


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def _eval_context(self):
        """Returns a dictionary to use as evaluation context for
           ir.rule domains.
           Note: company_ids contains the ids of the activated companies
           by the user with the switch company menu. These companies are
           filtered and trusted.
        """
        res = super(IrRule, self)._eval_context()
        res.update({'branch_ids': self.env.branch_ids.sudo().ids})
        return res


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        display_switch_branch_menu = user.has_group(
            'aspl_fitness_management_ee.group_multi_branches') and len(
            user.sudo().branch_ids.ids) > 1
        result = super(IrHttp, self).session_info()

        if request.httprequest.cookies.get('cids'):
            allowed_companies = [
                int(company) for company in request.httprequest.cookies.get(
                    'cids')
                if company.isnumeric()]
        else:
            allowed_companies = user.company_id.ids
        current_branch_id = False
        if request.httprequest.cookies.get('bids'):
            bids_lst = []
            company_set = set()
            current_branch_id = request.httprequest.cookies.get('bids')[0]
            for branch in request.httprequest.cookies.get('bids'):
                if branch.isnumeric():
                    branch_id = request.env[
                        'company.branch'].sudo().browse(int(branch))
                    if branch_id.exists():
                        bids_lst.append(int(branch))
                        company_set.add(int(branch_id.company_id.id))
            if len(bids_lst) <= 1 and user.sudo().branch_id.id not in bids_lst:
                bids_lst.append(user.sudo().branch_id.id)
            new_company_ids = list(set(allowed_companies) - company_set)
            if new_company_ids:
                company_ids = request.env[
                    'res.company'].sudo().browse(new_company_ids)
                if company_ids.exists():
                    bids_lst.extend(user.sudo().branch_ids.filtered(
                        lambda branch: branch.company_id.id in company_ids.ids
                    ).ids)
            allowed_branches = self.env[
                'company.branch'].sudo().browse(bids_lst).filtered(
                lambda x: x.company_id.id in allowed_companies).ids
            if request.httprequest.cookies.get('cids'):
                allowed_branches = self.env['company.branch'].sudo().search([
                    ('company_id', 'in', allowed_companies)]).ids
        else:
            allowed_branches = user.sudo().branch_ids.ids
            if allowed_branches:
                current_branch_id = allowed_branches[0]
        # Filter Branch with User Allow Branch
        allowed_branches = list(set(allowed_branches).intersection(user.sudo().branch_ids.ids))
        if allowed_branches:
            user.write({
                'current_branch_ids': [
                    (3, each.id) for each in user.current_branch_ids],
                # 'branch_ids': [(3, each.id) for each in user.branch_ids]
            })
            user.write({
                'current_branch_ids': [(4, each) for each in allowed_branches],
                # 'branch_ids': [(4, each.id) for each in self.env[
                #     'res.company'].browse(allowed_companies).mapped('branch_ids')
                #                if each.company_id.id in user.company_ids.ids]
            })

            result.update({
                'display_switch_branch_menu': user.has_group(
                    'aspl_fitness_management_ee.group_multi_branches') and len(
                    user.sudo().branch_ids) > 1,
                'branch_id': user.sudo().branch_id.id if request.session.uid
                else None,
                'user_branches': {
                    'current_branch': user.sudo().current_branch_ids and [
                        user.sudo().current_branch_ids[0].id] or [],
                    'allowed_branches': {
                        branch.id: {
                            'id': branch.id,
                            'name': branch.name,
                            'company_id': branch.company_id.id,
                        } for branch in user.sudo().current_branch_ids
                    },
                    'currentBranch': {
                        'id': user.sudo().branch_ids and user.sudo().branch_ids[
                            0].id or False,
                        'name': user.sudo().branch_ids and user.sudo(
                        ).branch_ids[0].name
                    }}
                if display_switch_branch_menu else False,
            })
            result.get('user_context').update({
                'allowed_branch_ids': allowed_branches
            })
        return result


# class Module(models.Model):
#     _inherit = "ir.module.module"
#
#     @assert_log_admin_access
#     def button_install(self):
#         res = super(Module, self).button_install()
#         self._cr.execute('''
#             select
#                 t.table_name
#             from
#                 information_schema.tables t
#             inner join information_schema.columns c on c.table_name = t.table_name
#                                             and c.table_schema = t.table_schema
#
#             where c.column_name = 'company_id' and t.table_schema in ('public')
#                   and t.table_type = 'BASE TABLE'
#             order by t.table_schema;
#         ''')
#         for each_module in self._cr.fetchall():
#             print('\n\n=======module result=======', each_module)
#             self._cr.execute('''
#                 ALTER TABLE
#                           %s
#                 ADD COLUMN  IF NOT EXISTS
#                            branch_id INTEGER,
#                 ADD FOREIGN KEY (branch_id)
#                 REFERENCES
#                            company_branch (id)
#                 ON DELETE SET NULL;
#             ''' % (each_module[0]))
#         return res
#

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
