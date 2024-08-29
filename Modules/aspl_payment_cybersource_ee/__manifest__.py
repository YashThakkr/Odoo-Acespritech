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
    'name': 'Odoo CyberSource Payment Gateway (Enterprise)',
    'summary': 'Cybersource Payment Gateway',
    'license': 'LGPL-3',
    'version': '17.0.1.0.0',
    'description': """Cybersource Payment Gateway""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Website',
    'website': "http://www.acespritech.com",
    'price': 55.00,
    'currency': 'EUR',
    'depends': ['base', 'web','payment','website_sale', 'mail', 'account_payment'],
    'data': [
        'views/payment_cybersource_template.xml',
        'views/payment_view.xml',
        'data/payment_provider_data.xml',
    ],
    'external_dependencies': {
        'python': [
            'suds'
        ],
    },
    'images': ['static/description/main_screenshot.jpg'],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend_lazy': [
            'aspl_payment_cybersource_ee/static/src/js/payment_form.js',
            'aspl_payment_cybersource_ee/static/src/css/style.css',
        ],
    },
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: