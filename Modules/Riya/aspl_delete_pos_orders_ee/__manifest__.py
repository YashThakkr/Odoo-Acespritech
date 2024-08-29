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
    'name': "POS Delete Orders (Enterprise)",
    'version': '1.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Point of Sale',
    'description': """
                This module allow delete paid Pos orders.
            """,
    'website': "http://www.acespritech.com",
    'price': 15.00,
    'currency': 'EUR',
    'summary': 'This module allow delete paid POS orders.',
    'depends': ['sale', 'point_of_sale', 'account', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/point_of_sale.xml',
        'wizard/pos_cancel_wizard.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    "installable": True,
    'auto_install': False,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
