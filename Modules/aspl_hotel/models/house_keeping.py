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


from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class WorkOrderCateg(models.Model):
    _name = "work.order.categ"
    _description = "work order category"

    name = fields.Char(string="Work Order Type")
    active = fields.Boolean(string='Active', default=True)
    is_cleaning = fields.Boolean(string='Cleaning')

    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())

    # @api.model_create_multi
    # def create(self, vals):
    #     cleaning_type_id = self.search([('is_cleaning', '=', True)])
    #     if vals.get('is_cleaning') and cleaning_type_id:
    #         raise UserError(_('You cannot have more then one cleaning type'))
    #     return super(WorkOrderCateg, self).create(vals)

    @api.model_create_multi
    def create(self, vals):
        print("\n\n vals", vals)
        res = super(WorkOrderCateg, self).create(vals)
        print("\n\n res", res)
        cleaning_type_id = self.search([('is_cleaning', '=', True)])
        print("\n\n cleaning_type_idss", cleaning_type_id)
        for record in res:
            if record.is_cleaning and cleaning_type_id:
                raise UserError(_('You cannot have more then one cleaning type'))
        return res


class MaintenanceBlock(models.Model):
    _name = "maintenance.block"
    _description = "maintenance block"
    _rec_name = "room_id"

    room_id = fields.Many2one('hotel.room', string="Room")
    block_from = fields.Date(string="Block From")
    block_until = fields.Date(string="Block Until")
    blocked_by_id = fields.Many2one('res.partner', string="Blocked By")
    reason_id = fields.Many2one('maintenance.block.reason', string="Reason")
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class MaintenanceBlockReason(models.Model):
    _name = "maintenance.block.reason"
    _description = "Maintenance Block Reason"

    name = fields.Char(string="Reason")
    active = fields.Boolean(string='Active', default=True)
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())


class HotelHouseStatus(models.Model):
    _name = "hotel.house.status"
    _rec_name = "room_id"
    _description = "Hotel House Status"

    room_id = fields.Many2one('hotel.room', string="Room")
    room_type_id = fields.Many2one(related="room_id.room_type_id", string="Room Type")
    status = fields.Selection([('clean', 'Clean'), ('dirty', 'Dirty'), ('occ', 'OCC'),
                               ('vac', 'VAC')], string="Status")
    availability = fields.Selection([('available', 'Available'), ('stayover', 'Stayover'),
                                     ('arrived', 'Arrived'), ('due_out', 'Due Out'), ('suite_block', 'Suite Block')],
                                    string="Availability")
    fd_remarks = fields.Text(string="FD Remarks")
    hk_remarks = fields.Text(string="HK Remarks")
    house_keeper_id = fields.Many2one('res.partner', string="Housekeeper")
    color = fields.Integer('Color Index', compute="change_color_on_kanban")

    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    @api.depends('status')
    def change_color_on_kanban(self):
        """    this method is used to change color index
        base on fee status    ----------------------------------------    
        :return: index of color for kanban view    """
        for record in self:
            color = 0
            if record.status == 'occ':
                color = 7
            elif record.status == 'vac':
                color = 5
            elif record.status == 'dirty':
                color = 1
            elif record.status == 'clean':
                color = 10
            else:
                color = 5
            record.color = color


class WorkOrderDetail(models.Model):
    _name = "work.order.detail"
    _description = "Work Order Detail"
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', 'Assign to')
    work_date = fields.Date('Date')
    work_order_line_ids = fields.One2many('work.order.line', 'work_order_id', 'Work Order Line')

    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    @api.constrains('user_id', 'work_date')
    def _check_user_for_today_work(self):
        for order in self:
            work_order_id = self.search(
                [('user_id', '=', order.user_id.id), ('id', '!=', order.id),
                 ('work_date', '=', order.work_date)], limit=1)
            if work_order_id and work_order_id.user_id:
                raise ValidationError("For this user today work order already created.")

    @api.model
    def search_today_work_order(self, today_date):
        start_date = datetime.strptime(today_date, '%m/%d/%Y').date()
        new_start_date = datetime.strftime(start_date, "%Y-%m-%d")
        work_order_list = []
        work_order_task_list = []
        task_dict = {}
        task_list = []
        uid = request.env.user.id
        if uid:
            work_order_id = self.sudo().search([('user_id', '=', int(uid)), ('work_date', '=', new_start_date)])
            for each_work_order in work_order_id:
                for each_work_order_line in each_work_order.work_order_line_ids:
                    if not each_work_order_line.work_order_categ_id.name in task_list:
                        task_list.append(each_work_order_line.work_order_categ_id.name)
                    if not each_work_order_line.room_id.room_no in task_dict:
                        task_dict[each_work_order_line.room_id.room_no] = {each_work_order_line.status: [
                            each_work_order_line.work_order_categ_id.name]}
                    else:
                        if not each_work_order_line.status in task_dict[each_work_order_line.room_id.room_no]:
                            task_dict[each_work_order_line.room_id.room_no][each_work_order_line.status] = [
                                each_work_order_line.work_order_categ_id.name]
                        else:
                            task_dict[each_work_order_line.room_id.room_no][each_work_order_line.status].append(
                                each_work_order_line.work_order_categ_id.name)

            return {'task_list': task_list,
                    'task_dict': task_dict,
                    'user_id': uid,
                    'task_list_len': len(task_list),
                    'user_name': request.env.user.name,
                    'work_order_id': work_order_id.id}
        return False


class WorkOrderLine(models.Model):
    _name = "work.order.line"
    _description = "Work Order Line"

    work_order_id = fields.Many2one('work.order.detail')
    room_id = fields.Many2one('hotel.room', string="Room")
    description = fields.Char('Description')
    work_order_categ_id = fields.Many2one('work.order.categ', string="Order Category")
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    work_duration = fields.Char('Duration(Minutes)')
    status = fields.Selection([('pending', 'Pending'), ('start', 'Start'), ('done', 'Done')], default='pending',
                              string='Status')
    remark = fields.Char(string="Remark")

    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    @api.model
    def write_work_order(self, room_id, user_id, task_name, work_order):
        domain = [('room_id.room_no', '=', room_id),
                  ('work_order_id', '=', int(work_order))]
        if task_name:
            domain += [('work_order_categ_id.name', '=', task_name)]
        print('\n\n-----domain', domain)
        order_line_id = self.sudo().search(domain)
        if order_line_id:
            order_line_id.write({'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                 'status': 'start'})
            return True
        return False


class ResUser(models.Model):
    _inherit = 'res.users'

    is_work_order = fields.Boolean('Is Work Order')
    # branch_id = fields.Many2one('company.branch', string="Branch")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
