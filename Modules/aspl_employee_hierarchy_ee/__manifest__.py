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
{
    'name': 'Employee Hierarchy (Enterprise)',
    'category': 'Employee',
    'description': """Employee Hierarchy""",
    'summary': 'See employee hierarchy if you are a manager',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'version': '17.0.1.0.0',
    'website': 'http://www.acespritech.com',
    'depends': ['base', 'base_setup', 'hr', 'mail', 'hr_attendance', 'project', 'hr_timesheet', 'im_livechat'],
    'price': 52.28,
    'currency': 'EUR',
    'images': ['/aspl_employee_hierarchy_ee/static/description/main_screenshot.png'],
    'assets': {
        'web.assets_backend': [
            '/aspl_employee_hierarchy_ee/static/src/xml/employee_hierarchy.xml',
            '/aspl_employee_hierarchy_ee/static/src/js/employee_hierarchy.js',
            '/aspl_employee_hierarchy_ee/static/src/css/main.css',
            ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
