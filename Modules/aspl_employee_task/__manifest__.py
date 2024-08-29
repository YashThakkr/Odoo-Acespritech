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
    'name': 'Employee Project Task (Community)',
    'category': 'Employee',
    'description': """Employee Project Task""",
    'summary': 'See employee task if you are a manager',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'version': '17.0.1.0.0',
    'website': 'http://www.acespritech.com',
    'images': ['/aspl_employee_leave/static/description/main_screenshot.png'],
    'depends': ['base', 'base_setup', 'hr', 'project'],
    'price': 0,
    'currency': 'EUR',
    'data': [
        'views/res_config_settings_view.xml',
        ],
    'assets': {
        'web.assets_backend': [
            '/aspl_employee_task/static/src/xml/employee_task.xml',
            '/aspl_employee_task/static/src/js/employee_task.js',
            '/aspl_employee_task/static/src/css/main.css',
            ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
