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
from odoo import http
from odoo.http import request


class EmployeeController(http.Controller):
    @http.route('/get/employee/data', type='json', auth='user')
    def search_leaves(self, **kwargs):
        result = []
        current_user = request.env.user
        manager_employee = request.env['hr.employee'].search([('user_id', '=', current_user.id)])
        if manager_employee:
            leaves = request.env['hr.leave'].search(
                [('employee_id.parent_id', '=', manager_employee.id), ('state', '=', 'confirm')])
            if leaves:
                for leave in leaves:
                    result.append({
                        'id': leave.id,
                        'name': leave.name,
                        'holiday_status_id': leave.holiday_status_id.name,
                        'start_date': leave.request_date_from,
                        'end_date': leave.request_date_to,
                        'days': leave.number_of_days_display,
                        'employee_ids': leave.employee_ids.name,
                        'emp_id': leave.employee_ids.id
                    })
                return [result]
            else:
                return [False]
        else:
            return [False]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
