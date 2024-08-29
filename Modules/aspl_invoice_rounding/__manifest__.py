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
    'name': 'Invoice Rounding (Community)',
    'version': '17.0.1.0.0',
    'category': 'Account',
    'summary': 'Rounding Invoice Amount',
    'description': """
        This module allows to round the total amount of invoice and also manage the Journal Entry for rounding amount..
        """,
    'price': 20.00,
    'currency': 'EUR',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'depends': ['base', 'account'],
    "data": [
        'views/res_config_view.xml',
        'views/account_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'aspl_invoice_rounding/static/src/**/*',
        ]},
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
