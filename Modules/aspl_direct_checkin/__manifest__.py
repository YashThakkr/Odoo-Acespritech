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
{
    'name': 'Direct Checkin (Community)',
    'version': '16.0.1.0.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'General',
    'description': """
        Module allows You to restrict the user/employee to checkin first after login.
    """,
    'website': 'http://www.acespritech.com',
    'price': 40,
    'currency': 'EUR',
    'summary': 'Module allows You to restrict the user/employee to checkin first after login.',
    'depends': ['base','hr','hr_attendance'],
    'images': ['static/description/main_screenshot.png'],
    'data': [
        'views/login.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: