# -*- coding: utf-8 -*-

{
    'name': 'Odoo Backend Automatic Logout',
    'version': '1.0',
    'category': 'All',
    'sequence': 6,
    'author': 'ErpMstar Solutions',
    'summary': 'Allows you to automatically logout when you do not interact with odoo.',
    'depends': ['web'],
    'data': [
        'views/view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_auto_logout/static/src/js/web.js',
        ],
    },
    'images': [
        'static/description/logout.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 25,
    'currency': 'EUR',
    'bootstrap': True,
}
