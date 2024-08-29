# -*- coding: utf-8 -*-
#################################################################################

{
    'name': 'Cash Receipt Voucher',

    'category': 'Uncategorized',
    
    'summary': 'This module allows custom cash receipt.',
    
    'description': """Custom report for cash receipt.""",
    
    'author': "My Company",
    
    'website': "https://www.yourcompany.com",
    
    'version': '0.1',
    
    'depends': ['base','account','account_accountant'],
    
    "data": [
        'reports/cash_report_voucher_view.xml',
        'views/payment_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}