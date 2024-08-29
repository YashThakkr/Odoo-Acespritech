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
    'name': 'Employee Leave (Enterprise)',
    'category': 'Employee Leave',
    'description': """Employee Leave""",
    'summary': 'See employee leave if you are a manager',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'version': '17.0.1.0.0',
    'website': 'http://www.acespritech.com',
    'images': ['/aspl_employee_leave_ee/static/description/main_screenshot.png'],
    'depends': ['base', 'hr', 'hr_holidays','hr_attendance'],
    'price': 30,
    'currency': 'EUR',
    'assets': {
        'web.assets_backend': [
            '/aspl_employee_leave_ee/static/src/js/employee_leave_hierarchy.js',
            '/aspl_employee_leave_ee/static/src/css/main.css',
            '/aspl_employee_leave_ee/static/src/xml/employee_leave_hierarchy.xml',
            ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
