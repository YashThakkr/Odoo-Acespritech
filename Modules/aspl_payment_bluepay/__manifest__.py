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
    'name': 'BluePay Payment Gateway Service(Community)',
    'version': '15.0.1.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Account',
    'description': """BluePay Payment Gateway Service
    """,
    'website': 'http://www.acespritech.com',
    'price': 55,
    'currency': 'EUR',
    'license': 'LGPL-3',
    'summary': 'BluePay Payment Gateway Service',
    'depends': ['base', 'website_sale'],
    'data': [
        'views/payment_bluepay_templates.xml',
        'views/payment_acquirer.xml',
        'views/payment_bluepay_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    "assets": {
        'web.assets_frontend': [
            # 'aspl_payment_bluepay/static/src/js/bluepay_checkout.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
