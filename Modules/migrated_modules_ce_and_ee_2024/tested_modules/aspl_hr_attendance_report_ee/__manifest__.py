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
    'name': 'HR Attendance Report (Enterprise)',
    'version': '1.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'HR',
    'description': """
        Module allows to Print report from Hr Attendance.
    """,
    'website': 'http://www.acespritech.com',
    'price': 30,
    'currency': 'EUR',
    'license': 'AGPL-3',
    'summary': 'Module allows to print report from Hr Attendance.',
    'depends': ['base', 'hr', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/attendance_report_wizard.xml',
        'report/attendance_report_pdf.xml',
        'report/attendance_reports.xml',

    ],
    'images': ['static/description/main_screenshot.jpg'],
    'installable': True,
    'auto_install': False,
    'license' : 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
