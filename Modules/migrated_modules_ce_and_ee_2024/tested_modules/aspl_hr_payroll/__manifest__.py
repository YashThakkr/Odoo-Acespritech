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
    'name': 'Odoo Payroll (Community)',
    'category': 'Human Resources',
    'summary': 'Manage your employee payroll records',
    'website': 'http://www.acespritech.com',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'description': "Payroll",
    'depends': [
        'base',
        'hr_contract',
        'hr_holidays',
    ],
    'price': 70,
    'currency': 'EUR',
    'data': [
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'data/hr_payroll_sequence.xml',
        'data/hr_payroll_data.xml',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payroll_report.xml',
        'wizard/hr_payroll_contribution_register_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_contributionregister_templates.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslipdetails_templates.xml',
    ],
    'images': ['/aspl_hr_payroll_ee/static/description/main_screenshot.png'],
    'demo': ['data/hr_payroll_demo.xml'],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    # 'version': '16.0.1.0.1'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: