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
    'name': 'User RFID Login (Enterprise)',
    'summary': 'User RFID Login',
    'version': '16.0.1.0.0',
    'description': """User can Login with RFID Card""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'General',
    'price': 125.00,
    'currency': 'EUR',
    'website': "http://www.acespritech.com",
    'depends': ['base', 'base_setup', 'web'],
    'data': [
        'views/login.xml',
        'views/res_users.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'aspl_auth_rfid_login_ee/static/src/css/frontend_css.css',
            'aspl_auth_rfid_login_ee/static/src/js/jquery.rfid.js',
            'aspl_auth_rfid_login_ee/static/src/js/user_login.js',
        ],
    },
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
