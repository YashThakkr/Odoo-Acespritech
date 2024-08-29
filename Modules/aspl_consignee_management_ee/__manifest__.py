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
    'name': 'Stock Consignee Management (Community)',
    'version': '17.0.1.0.0',
    'summary': 'Stock Consignee Management',
    'description': "Stock Consignee Management",
    'category': 'Stock',
    'price': 49,
    'currency': 'EUR',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'depends': ['base', 'stock', 'sale', 'sale_management', 'mail', 'product_expiry', 'sales_team'],
    'images': ['static/description/main_screenshot.png'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/stock_consignee_report_view.xml',
        'report/sale_consignee_report_view.xml',
        'report/stock_consignee_transfer_report.xml',
        'report/report_view.xml',
        'data/stock_consignee_data.xml',
        'data/mail_template_data.xml',
        'views/stock_consignee_view.xml',
        'views/sale_consignee_consume_view.xml',
        'views/res_config_settings_view.xml',
        'views/res_partner_view.xml',
        'wizard/stock_consignee_wiz_view.xml',
        'wizard/consignee_import_transfer_wiz.xml',
        'report/consignee_report_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
