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
    'name': 'Float Slider (Community)',
    'version': '1.0',
    'category': 'All',
    'summary': "Float slider helps you to add range widget in float field.",
    'description': "Float slider helps you to add range widget in float field.",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    "depends": ['web','base'],
    'currency': 'EUR',
    'price': 20.00,
    "data": [
        'partner/partner_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'aspl_float_slider/static/src/js/widget.js',
            'aspl_float_slider/static/src/xml/widget.xml',
        ],
    },
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

