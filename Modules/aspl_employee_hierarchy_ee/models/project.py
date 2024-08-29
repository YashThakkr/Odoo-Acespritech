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
from odoo import models, fields, _


class TaskEmployee(models.Model):
    _inherit = "project.task"

    def get_projectview_action(self, employee):
        view_id = self.sudo().get_formview_id(access_uid=employee)
        employee_id = self.env['hr.employee'].browse(employee)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'name': 'Tasks',
            'view_type': 'kanban',
            'view_mode': 'kanban,list,form',
            'views': [[False, 'kanban', view_id], [False, 'list', view_id], [False, 'form', view_id]],
            'res_id': self.id,
            'context': dict(self._context),
            'domain': [('user_ids', 'in', employee_id.user_id.id)]
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: