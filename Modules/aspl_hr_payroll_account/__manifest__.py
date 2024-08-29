#-*- coding:utf-8 -*-
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
    'name': 'Odoo Payroll Accounting (Community)',
    'category': 'Human Resources',
    'website': 'http://www.acespritech.com',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'description': """
Generic Payroll system Integrated with Accounting.
==================================================

    * Expense Encoding
    * Payment Encoding
    * Company Contribution Management
    """,
    'price': 75,
    'currency': 'EUR',
    'depends': ['aspl_hr_payroll', 'account'],
    'data': ['views/hr_payroll_account_views.xml'],
    # 'demo': ['data/hr_payroll_account_demo.xml'],
    'test': ['../account/test/account_minimal_test.xml'],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    # 'version': '16.0.1.0.1'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
