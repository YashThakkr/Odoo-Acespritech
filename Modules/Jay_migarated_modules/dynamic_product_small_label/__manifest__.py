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
    'name': "Dynamic Product Small Label (Community)",
    'version': '17.1',
    'category': 'Product',
    'description': """
        User can create custom label template by frontend and can print the dynamic product label report.
    """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'summary': 'Create custom label template and print dynamic product label report.',
    'depends': ['base', 'sale_management', 'purchase', 'stock', 'account', 'mail'],
    'price': 100,
    'currency': 'EUR',
    'data': [
         'data/design_data.xml',
         'security/ir.model.access.csv',
         'report/prod_small_lbl_rpt.xml',
         'report/product_small_fields_label.xml',
         'views/dynamic_product_small_label_report.xml',
         'views/product_small_label.xml',
         'wizard/wizard_product_small_label_report.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
