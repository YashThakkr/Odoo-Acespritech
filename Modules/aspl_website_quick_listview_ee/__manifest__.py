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
    'name': 'Odoo Website Quick List View (Enterprise)',
    'summary': 'This module provides user to quick add products in to cart.',
    'version': '17.0.1.0.0',
    'description': "This module provides user to quick add products in to cart.",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'category': 'Website',
    'website': 'http://www.acespritech.com',
    'price': 14,
    'currency': 'EUR',
    'depends': ['website_sale', 'web'],
    'data': [
        'views/templates.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'aspl_website_quick_listview_ee/static/**/*',
        ],
    },
    'images': ['static/description/main_screenshot.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
