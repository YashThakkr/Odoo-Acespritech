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
    'name': 'SagePay Payment Provider (Community)',
    'category': 'Website',
    'summary': 'Payment Provider: SagePay Implementation',
    'version': '17.0.1.0.0',
    'price': 40.00,
    'currency': 'EUR',
    'license': 'LGPL-3',
    'description': """SagePay Payment Provider""",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "http://www.acespritech.com",
    'depends': ['base', 'payment', 'website_sale'],
    'images': ['static/description/main_screenshot.png'],
    'data': [
        'views/sagepay.xml',
        'views/payment_provider.xml',
        'data/sagepay_data.xml'
    ],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
