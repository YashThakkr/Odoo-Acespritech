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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
