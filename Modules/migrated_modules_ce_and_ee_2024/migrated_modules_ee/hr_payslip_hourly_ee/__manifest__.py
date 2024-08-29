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
    'name': 'HR Payslip Hourly (Enterprise)',
    'version': '1.0',
    'summary': "Calculate employee wage based on working Hours",
    'description': """Calculate employee wage based on working Hours""",
    'category': 'HR Payroll',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'currency': 'EUR',
    'price': 20,
    'depends': ['base', 'hr', 'hr_attendance', 'hr_contract', 'aspl_hr_payroll_ee'],
    'data': [
        'views/hr_payroll_view.xml',
        'views/hr_payroll_data.xml'
    ],
    'images': ['static/description/main_screenshot.jpg'],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: