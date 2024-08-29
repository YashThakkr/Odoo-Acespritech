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
    'name': "Daily Invoice Report (Enterprise)",
    'summary': "This report will show daily invoices of customer "
               "grouped by sale teams.",
    'version': "17.0.1.0.0",
    'description': """
        This report will show daily invoices of customer
                grouped by sale teams.
    """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Accounting',
    'website': 'http://www.acespritech.com',
    'price': 20,
    'currency': 'EUR',
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base', 'account', 'sale', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/report.xml',
        'wizard/daily_invoice_view.xml',
        'report/daily_invoice_report_template.xml',
    ],
    'auto_install': False,
    'installable': True,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
