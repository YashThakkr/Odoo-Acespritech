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
    'name': 'Website Account Payment (Enterprise)',
    'category': 'Payment',
    'summary': 'Account Payment',
    'description': """Account Payment""",
    'price': 25,
    'currency': 'EUR',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'version': '17.0.1.0.0',
    'depends': ['account_payment', 'website'],
    'images': ['static/description/main_screenshot.png'],
    "data": [
        "views/account_payment_view.xml",
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
