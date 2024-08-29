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
    'name': 'Hobex Payment (Community)',
    'category': 'General',
    'summary': 'Hobex Payment Getway',
    'description': """
        Hobex Payment Getway.
    """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'version': '17.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'website_sale', 'web', 'mail', 'account_payment'],
    'price': 52.00,
    'currency': 'EUR',
    'images': ['static/description/main_screenshot.png'],
    "data": [
        'views/template.xml',
        'views/payment_view.xml',
        'data/hobex_payment_provider.xml',

    ],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'aspl_payment_hobex/static/src/js/main.js',
        ],
    },
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
