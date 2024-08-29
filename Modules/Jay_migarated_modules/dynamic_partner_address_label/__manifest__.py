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
    'name': "Dynamic Partner Address Label (Community)",
    'version': '17.1',
    'category': 'general',
    'description': """Dynamic Partner Address Label.""",
    'summary': 'Create custom page label template by frontend and print dynamic partner address label report.',
    'author': 'Acespritech Solutions Pvt.Ltd',
    'website': 'http://www.acespritech.com',
    "depends": ['base', 'purchase', 'stock', 'account', 'sale_management'],
    'price': 99,
    'currency': 'EUR',
    "data": [
        'data/partner_design_data.xml',
        'page_reports.xml',
        'security/ir.model.access.csv',
        'views/dynamic_partner_page_rpt.xml',
        'views/wizard_partner_page_report_view.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'license' : 'LGPL-3',
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
