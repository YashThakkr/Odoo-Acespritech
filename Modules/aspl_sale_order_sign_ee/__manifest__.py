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
    'name': 'Sale Order Signature (Enterprise)',
    'category': 'Sales',
    'summary': 'This module allows user to sign sale order.',
    'description': """
This module allows user to sign sale order.
""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 15.00, 
    'currency': 'EUR',
    'version': '17.0.1.0.0',
    'depends': ['base','sale_management'],
    'images': ['static/description/main_screenshot.jpg'],
    "data": [
        'views/sales_config_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: