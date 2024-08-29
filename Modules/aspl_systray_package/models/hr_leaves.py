# -*- coding: utf-8 -*-
##############################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
##############################################################################
from odoo import fields,models,api


class HrLeaves(models.Model):
    _inherit = 'hr.leave'

    def action_change_status(self):
        if self.state == 'confirm':
            self.state = 'validate'

    def action_refuse_status(self):
        if self.state == 'confirm':
            self.state = 'refuse'

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        user_obj = self.env['res.users'].search([])
        user_list = [[user.partner_id, 'update.list', {'render': True}] for user in user_obj]
        self.env['bus.bus']._sendmany(user_list)
        return res

    def write(self, vals):
        res = super().write(vals)
        user_obj = self.env['res.users'].search([])
        user_list = [[user.partner_id, 'update.list', {'render': True}] for user in user_obj]
        self.env['bus.bus']._sendmany(user_list)
        return res

    def unlink(self):
        res = super().unlink()
        user_obj = self.env['res.users'].search([])
        user_list = [[user.partner_id, 'update.list', {'render': True}] for user in user_obj]
        self.env['bus.bus']._sendmany(user_list)
        return res

    def get_employee_leave_view(self, leaveId):
        leave_id = self.env['hr.leave'].browse(leaveId)
        view_id = self.sudo().get_formview_id(access_uid=leaveId)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'name': 'All Time Off',
            'view_type': 'form',
            'view_mode': 'form,list,kanban',
            'views': [[False, 'form', view_id], [False, 'list', view_id], [False, 'kanban', view_id]],
            'res_id': leave_id.id,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
