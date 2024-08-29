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
    'name': 'HR Overtime (Community)',
    'version': '1.0',
    'summary': 'HR Overtime',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Human Resources',
    'website': 'http://www.acespritech.com',
    'description': """HR Overtime""",
    'price': 20,
    'currency': 'EUR',
    'depends': ['base', 'hr', 'aspl_hr_payroll', 'hr_attendance', 'hr_contract', 'hr_timesheet', ],
    'images': ['static/description/main_screenshot.png'],
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'data/overtime_schedular.xml',
        'data/hr_employee_overtime_data.xml',
        'data/payroll_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_employee_overtime_views.xml',
        'views/hr_payslip_views.xml',
        'views/view_overtime_request.xml',
        'views/res_config_views.xml',
        'wizard/overtime_wizard.xml',
        'report/overtime_report_pdf.xml',
        'report/view_overtime_report.xml',
    ],
    'installable': True,
    'license' : 'LGPL-3',
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
