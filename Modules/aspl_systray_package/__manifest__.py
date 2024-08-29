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
    'name': 'Employee Systray Package (Community)',
    'category': 'Employee Systray Package',
    'description': """Employee Systray Package""",
    'summary': 'See employee hierarchy, leave and task if you are a manager',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'version': '17.0.1.0.0',
    'website': 'http://www.acespritech.com',
    'depends': ['base', 'hr', 'mail', 'hr_attendance', 'project','hr_holidays', 'hr_timesheet'],
    'price': 0,
    'currency': 'EUR',
    'images': ['/aspl_systray_package/static/description/main_screenshot.png'],
    'data': [
        'views/res_config_settings_view.xml',
        ],
    'assets': {
        'web.assets_backend': [
            '/aspl_systray_package/static/src/xml/employee_systary.xml',
            '/aspl_systray_package/static/src/js/systray_package.js',
            '/aspl_systray_package/static/src/css/main.css',
            ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
