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
    'name': 'Odoo Partner Map (Community)',
    'category': 'Base',
    'summary': 'Load Map in one window using different filter option in customer.',
    'description': """
                Load Map in one window using different filter option in customer.
            """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 20.00, 
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': ['base', 'sale_management'],
    'images': ['static/description/main_screenshot.png'],
    "data": [
            'security/ir.model.access.csv',
            'views/partner_search_map_view.xml',
            'views/res_partner_view.xml',
            'views/res_config_setting.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'partner_search_map/static/src/js/customer_map.js',
            'partner_search_map/static/src/js/markerclusterer.js',
            'partner_search_map/static/src/js/action_service.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
