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
    'name': 'Website Fast Order (Community)',
    'version': '17.0.1.0.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'website',
    'description': """
        Module allows user to place Fast Order by Uploading CSV, xls, xlsx Or by entering Product Code and Quantity or by selection products in list.
    """,
    'website': 'http://www.acespritech.com',
    'price': 25,
    'currency': 'EUR',
    'summary': 'Module allows user to place Fast Order by Uploading CSV, xls, xlsx Or by entering Product Code and Quantity or by selection products in list.',
    'depends': ['base', 'sale', 'website_sale', 'purchase'],
    'data': [
        'views/templates.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'assets': {
            'web.assets_frontend': [
                'aspl_website_fast_order/static/**/*',
            ],
        },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
