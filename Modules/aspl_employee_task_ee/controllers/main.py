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
    def get_employee_data(self):
        user_id = request.env.user.id
        task_ids = request.env['project.task'].search([('user_ids', '=', user_id)])
        task_list = []
        time_limit = request.env['ir.config_parameter'].sudo().get_param('aspl_employee_task_ee.time_count')
        for task_id in task_ids:
            task_list.append({
                'name': task_id.name,
                'id': task_id.id,
                'time_limit': time_limit,
                'project': task_id.project_id.name,
                'deadline': task_id.date_deadline,
                'user': [user.name for user in task_id.user_ids],
                'priority': task_id.priority
            })
        return task_list

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
