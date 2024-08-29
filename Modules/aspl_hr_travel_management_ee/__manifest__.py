# -*- coding: utf-8 -*-
##################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)          #
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.                     #
# All Rights Reserved.                                                           #
#                                                                                #
# This program is copyright property of the author mentioned above.              #
# You can`t redistribute it and/or modify it.                                    #
#                                                                                #
##################################################################################
{
    'name': 'Employee Travel Management & Expenses (Enterprise)',
    'version': '16.0.1.0.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'summary': 'Manage Employee Travel Request & Expense',
    'description': """Employee Travel Request & Expense Module Manage the Travelling Expense.""",
    'category': 'General',
    'website': 'https://www.acespritech.com',
    'depends': ['base', 'hr', 'hr_expense','project'],
    'images': ['static/description/main_screenshot.png'],
    'price': 35,
    'currency': 'EUR',
    'data': [
        "security/aspl_hr_travel_management_security.xml",
        "security/ir.model.access.csv",
        "data/aspl_hr_travel_management_sequences.xml",
        "data/aspl_hr_travel_management_mail_templates.xml",
        "views/res_config_settings_views.xml",
        "views/hr_employee_view.xml",
        "views/emp_grade_expense_view.xml",
        "views/emp_grade_view.xml",
        "views/emp_travel_request_view.xml",
        "views/employee_proposed_expenses_view.xml",
        "views/emp_travel_place_view.xml",
        "views/emp_multi_currency_view.xml",
        "views/menu_views.xml",
        "wizard/hr_travel_reason_wizard.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'aspl_hr_travel_management_ee/static/src/js/web.js',
        ],
        'images': ['static/description/main_screenshot_ee.png'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
