{
    'name': 'Dics Sale Order Bulk Confirm',
    'version': '16 .0.0.0',
    'author': 'DataInteger Consultancy Services LLP',
    'maintainer': 'DataInteger Consultancy Services LLP',
    'company': 'DataInteger Consultancy Services LLP',
    'website': 'https://www.datainteger.com',
    'category': '',
    'summary': '',
    'description': "",
    'depends': ['sale', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizard/confirm_wiz_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
# -*- coding: utf-8 -*-
