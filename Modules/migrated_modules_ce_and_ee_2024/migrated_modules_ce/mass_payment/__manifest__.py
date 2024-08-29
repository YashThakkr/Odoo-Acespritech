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
    'name': 'Mass Payments (Community)',
    'version': '1.0',
    'category': 'Accounting',
    'description': """User can do mass payments to vendors and receive payments from customers.""",
    'summary': 'User can do mass payments to vendors and receive payments from customers.',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'depends': ['base', 'account'],
    'price': 30,
    'currency': 'EUR',
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'report/report.xml',
        'report/report_mass_payment.xml',
        'views/account_payment_view.xml',
        'views/mass_payment_view.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/main_screenshot.jpg'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: