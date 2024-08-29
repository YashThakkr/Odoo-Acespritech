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
    'name': 'Odoo Website Gift Card (Community)',
    'summary': 'This module allows user to purchase giftcard,use giftcard and also recharge giftcard.',
    'version': '17.0.1.0.0',
    'description': """This module allows user to purchase giftcard,use giftcard and also recharge giftcard.""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Website',
    'website': "http://www.acespritech.com",
    'price': 35,
    'currency': 'EUR',
    'depends': ['base', 'website_sale', 'sale_management', 'website', 'uom'],
    'data': [
        'security/ir.model.access.csv',
        'views/gift_card.xml',
        'views/gift_card_mail_template.xml',
        'views/gift_card_backend_view.xml',
        'views/res_config_view.xml',
        'wizard/add_gift_card_wizard_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'aspl_website_gift_card/static/src/js/card_detail.js',
            'aspl_website_gift_card/static/src/js/jquery.validate.min.js',
            'aspl_website_gift_card/static/src/js/main.js',
            'aspl_website_gift_card/static/src/css/main.css',
        ],
    },
    'license': 'LGPL-3',
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
