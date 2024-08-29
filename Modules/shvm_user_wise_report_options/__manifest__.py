# -*- coding: utf-8 -*-
# Email: sales@creyox.com
{
    'name': 'User wise report printing options | Direct print the report | Direct open the report',
    "author": "Creyox Technologies",
    'sequence': '1',
    'version': '16.0.1',
    'price': '39.0',
    'currency': 'USD',
    'summary': "It helps to print, download, or open the report user-wise.",
    'description':
        """User can direct open or print the report.""",
    "license": "LGPL-3",
    'depends': ['web'],
    'data': [
        'views/res_users_form_view.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'web.assets_backend': [
            ('replace', 'web/static/src/webclient/actions/action_service.js', 'shvm_user_wise_report_options/static/src/js/action_service.js'),
        ],
    },
}
