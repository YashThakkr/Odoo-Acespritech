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
    'name': 'Website Invoice Signature (Enterprise)',
    'category': 'Invoice',
    'summary': 'Website Invoice Signature',
    'description': """Website Invoice Signature
""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'version': '17.0',
    'price': 30,
    'currency': 'EUR',
    'depends': ['payment', 'portal', 'account_payment', 'account', 'website'],
    'images': ['static/description/main_screenshot.png'],
    "data": [
        'views/account_portal_templates.xml',
        'views/report_invoice.xml',
        'views/account_move_view.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'aspl_website_invoice_signature_ee/static/**/*',
    #     ],
    # },
    'license' : 'LGPL-3',
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
