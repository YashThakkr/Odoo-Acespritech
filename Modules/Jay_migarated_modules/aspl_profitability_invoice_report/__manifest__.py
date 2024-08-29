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
    'name': 'Profitability By Invoice Report (Community)',
    'category': 'Account',
    'version': '17.1',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'summary': 'This module allows you to generate Profitability By Invoice Report(PDF) base on entered dates, customers,sales teams and products.',
    'description': '''This module allows you to generate Profitability By Invoice Report(PDF) base on entered dates, customers,sales teams and products.''',
    'price': 30.00,
    'currency': 'EUR',
    'depends': ['base', 'sale_management', 'purchase', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/profitability_invoice_wiz_view.xml',
        'report/report.xml',
        'report/report_profitability_by_invoice_temp_view.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
