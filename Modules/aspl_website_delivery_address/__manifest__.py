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
    'name': 'Multiple Delivery Address with Website (Community)',
    'summary': 'This module allows user to use multiple delivery address for orders.',
    'version': '17.0.1.0',
    'description': """This module allows user to use multiple delivery address for orders.""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Website',
    'website': "http://www.acespritech.com",
    'price': 45,
    'currency': 'EUR',
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base', 'website_sale', 'sale_management', 'website', 'stock'],
    'data': [
        'views/web_site_sale_inherited.xml',
        'views/sale_order_view.xml',
        'views/templates.xml',
    ],
    'assets': {
            'web.assets_frontend': [
                'aspl_website_delivery_address/static/**/*',
                #'aspl_website_delivery_address/static/src/js/components/**/*',
                # 'aspl_website_delivery_address/static/src/css/main.css',
                # 'aspl_website_delivery_address/static/src/scss/main.scss',
                # 'aspl_website_delivery_address/static/src/js/website_sale_delivery.js',
                # 'aspl_website_delivery_address/static/src/js/website_delivery_dialog.js',
            ],
        },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
