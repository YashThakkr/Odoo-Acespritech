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


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def get_timesheetview_action(self, employee):
        employee_id = self.env['hr.employee'].browse(employee)
        view_id = self.sudo().get_formview_id(access_uid=employee)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'name': 'Timesheet',
            'view_type': 'list',
            'view_mode': 'list,kanban,form',
            'views': [[False, 'list', view_id], [False, 'kanban', view_id], [False, 'form', view_id]],
            'res_id': self.id,
            'context': dict(self._context),
            'domain': [('employee_id', '=', employee_id.id)]
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: