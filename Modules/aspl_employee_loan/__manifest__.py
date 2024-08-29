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
    'name': 'Employee Loan (Community)',
    # 'version': '16.0.1.0.1',
    'summary': "This module manage employee loan and integrate with payroll.",
    'category': 'General',
    'description': """
        This module manage employee loan and integrate with payroll.
        """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 35.00,
    'currency': 'EUR',
    'depends': ['base', 'sale', 'account', 'hr', 'aspl_hr_payroll', 'aspl_hr_payroll_account'],
    'images': ['static/description/main_screenshot.png'],
    'data': [
        'views/report.xml',
        'views/loan_data.xml',
        'views/loan_type_view.xml',
        'views/loan_application_view.xml',
        'views/loan_calc_view.xml',
        'views/hr_payroll_view.xml',
        'views/loan_setting_view.xml',
        'views/wizard_loan_reject_view.xml',
        'security/ir.model.access.csv',
        'security/loan_security.xml',
        'views/report_loan_summary.xml',
        'views/mail_template_view.xml',
        'views/report_loan_contract.xml',
        'views/loan_prepayment_view.xml',
        'views/loan_advance_payment_view.xml',
        'views/loan_adjustment_view.xml',
        'views/hr_payroll_data.xml'
    ],
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['num2words','numpy','numpy_financial'],
    },
    'installable': True,
    'auto_install': False,
}
