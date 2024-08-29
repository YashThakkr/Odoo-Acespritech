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
    "name" : "HR Advance Salary (Enterprise)",
    'summary' : "HR Advance Salary (Enterprise)",
    "version" : "1.0",
    "description": """HR Advance Salary""",
    'author' : 'Acespritech Solutions Pvt. Ltd.',
    'category' : 'HR',
    'website' : 'http://www.acespritech.com',
    'price': 30,
    'currency': 'EUR',
    'images': ['static/description/main_screenshot.png'],
    "depends": ['base', 'hr', 'hr_payroll_account',
                 'hr_contract','web', 'payslip_payment_app'],
    'images': ['static/description/main_screenshot.png'],
    "data": [
        'views/hr_adv_salary_req_data.xml',
        'views/hr_salary_sheet_view.xml',
        'views/hr_adv_salary_req_view.xml',
        'views/hr_employee_view.xml',
        'views/account_move_view.xml',
        'views/reject_reason_view.xml',
        'views/hr_payroll_data.xml',
        'views/hr_payroll_view.xml',
        'views/advance_salary_req_template.xml',
        'views/disburse_amt_wiz_view.xml',
        'views/summary_wiz_view.xml',
        'views/template_summary_wiz.xml',
        'views/report.xml',
        'security/security_view.xml',
        'security/ir.model.access.csv',
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: