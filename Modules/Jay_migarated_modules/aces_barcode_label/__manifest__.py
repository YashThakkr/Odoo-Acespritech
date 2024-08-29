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
    'name': 'Product Barcode Label (Community)',
    'version': '17.1',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Product',
    'description': """
        Module allows to change the sequence of fields to display in barcode label report.
    """,
    'website': 'http://www.acespritech.com',
    'price': 55,
    'currency': 'EUR',
    'summary': 'Module allows to change the sequence of fields to display in barcode label report.',
    'depends': ['base', 'sale_management', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/aces_small_barcode_label_view.xml',
        'report/aces_barcode_label_report.xml',
        'report/product_barcode_report_template.xml',
        'wizard/aces_small_barcode_lable_wizard_view.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
