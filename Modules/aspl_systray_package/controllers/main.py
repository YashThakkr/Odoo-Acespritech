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
    def get_employee_hierarchy(self):
        manager_id = request.env.user.employee_parent_id
        child_ids = request.env.user.employee_id.child_ids
        hierarchy_dict = {}
        if manager_id:
            hierarchy_dict.update({'manager_id': manager_id.id, 'manager_name': manager_id.name,
                                   # 'image': manager_id.image_1920,
                                   'current_employee': {'id': request.env.user.employee_id.id,
                                                        'name': request.env.user.employee_id.name,
                                                        # 'image': request.env.user.employee_id.image_1920,
                                                        'job_title': request.env.user.employee_id.job_title,
                                                        'child_count': len(child_ids),
                                                        'link': '/mail/view?model=%s&res_id=%s' %
                                                                ('hr.employee.public', request.env.user.employee_id.id),
                                                        'availability': request.env.user.employee_id.hr_presence_state
                                                        },
                                   'child_ids': {},
                                   'job_title': manager_id.job_title,
                                   'child_count': len(child_ids),
                                   'link': '/mail/view?model=%s&res_id=%s' %
                                           ('hr.employee.public', manager_id.id),
                                   'availability': request.env.user.employee_parent_id.hr_presence_state
                                   })
        else:
            hierarchy_dict.update({'current_employee': {'id': request.env.user.employee_id.id,
                                                        'name': request.env.user.employee_id.name,
                                                        # 'image': request.env.user.employee_id.image_1920,
                                                        'job_title': request.env.user.employee_id.job_title,
                                                        'child_count': len(child_ids),
                                                        'link': '/mail/view?model=%s&res_id=%s' %
                                                                ('hr.employee.public', request.env.user.employee_id.id),
                                                        'availability': request.env.user.employee_id.hr_presence_state
                                                        },
                                   'child_ids': {}
                                   })
        if child_ids:
            for child in child_ids:
                is_create_user = False
                if child.user_id:
                    is_create_user = True
                hierarchy_dict['child_ids'].update({child.id: {'name': child.name,
                                                               'is_create_user': is_create_user,
                                                               'id': child.id,
                                                               # 'image': child.image_1920,
                                                               'job_title': child.job_title,
                                                               'child_count': len(child.child_ids),
                                                               'link': '/mail/view?model=%s&res_id=%s' %
                                                                       ('hr.employee.public',
                                                                        child.id),
                                                               'availability': child.hr_presence_state
                                                               },
                                                    })
        return [hierarchy_dict]

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

    def get_employee_task(self):
        user_id = request.env.user.id
        task_ids = request.env['project.task'].search([('user_ids', '=', user_id)])
        task_list = []
        for task_id in task_ids:
            task_list.append({
                'name': task_id.name,
                'id': task_id.id,
                'project': task_id.project_id.name,
                'deadline': task_id.date_deadline,
                'user': [user.name for user in task_id.user_ids],
                'priority': task_id.priority
            })
        return task_list

    @http.route('/get/employee/systray', type='json', auth='user')
    def get_employee_systray(self):
        employee_hierarchy = self.get_employee_hierarchy()
        employee_task = self.get_employee_task()
        employee_leave = self.search_leaves()
        time_limit = request.env['ir.config_parameter'].sudo().get_param('aspl_systray_package.time_count')
        res = [employee_hierarchy, employee_task, employee_leave, time_limit]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
