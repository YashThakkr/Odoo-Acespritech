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
    'name': 'Custom Picking Report (Enterprise)',
    'version': '17.0.1.0.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Inventory',
    'description' :"""You can see total quantity in picking operation and delivery slip report and also you can do the signature.""",
    'website': "http://www.acespritech.com",
    'price': 15,
    'currency': 'EUR',
    'summary': 'You can see total quantity in picking operation and delivery slip report and also you can do the signature.',
    'depends' : ['base', 'stock'],
    'data' : [
        'report/report_custom_deliveryslip.xml',
        'report/report_stockpicking_operation.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
