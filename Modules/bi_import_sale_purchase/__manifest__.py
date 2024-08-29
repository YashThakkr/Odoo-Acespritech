# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Sales and Purchase Order from Excel or CSV File',
    'version': '16.0.0.1',
    'sequence': 4,
    'category': 'Sales',
    'summary': 'import sale order import sales order import sale data import SO excel import sale order from excel import sales order from csv import bulk sales import purchase order import po xls import purchases import purchase from excel import purchase order from csv',
    'description': """
        Easy to Import multiple sales order with multiple sales order lines on Odoo by Using CSV/XLS file and Easy to Import multiple purchase order with multiple purchase order lines on Odoo by Using CSV/XLS file
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    "price": 22,
    "currency": 'EUR',
    'depends': ['base','sale','sale_management','purchase'],
    'data': [
            'security/ir.model.access.csv',
            'view/sale.xml',
            'view/purchase_invoice.xml',
            "data/attachment_sample_sale.xml",
            ],
	'qweb': [],
    'demo': [],
    'test': [],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/0MMimkGK8u4',
    "images":['static/description/Banner.gif'],
}
