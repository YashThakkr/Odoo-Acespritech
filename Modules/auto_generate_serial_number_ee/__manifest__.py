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
    'name': 'Auto Generate Lot/Serial Number (Enterprise)',
    'version': '16.0.1.0.0',
    'summary': 'Auto Lot/Generate Serial Number',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Inventory',
    'description': """Generate serial numbers""",
    'website': "http://www.acespritech.com",
    'price': 20.00,
    'currency': 'EUR',
    'depends': ['base', 'stock', 'purchase'],
    'data': [
        'views/auto_generate_serial_number_on_wizard.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
