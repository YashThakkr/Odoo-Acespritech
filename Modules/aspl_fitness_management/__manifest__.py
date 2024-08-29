# coding=utf-8
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
    'name': 'Fitness Management (Community)',
    'category': 'General',
    'version': '16.0.1.0.0',
    'description': """
        Fitness Management
    """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'currency': 'EUR',
    'price': 490.00,
    'images': ['static/description/main_screenshot.png'],
    'depends': [
        'base', 'sale', 'purchase', 'hr', 'contacts', 'product', 'mail', 'stock',
        'sale_management', 'account', 'website',
        'sale_stock', 'purchase_stock', 'resource'],
    'data': [
        'security/branch_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/menu_view.xml',
        'views/account_view.xml',
        'views/res_company_view.xml',
        'views/branch_view.xml',
        'views/templates.xml',
        'views/equipment_view.xml',
        'views/gym_view.xml',
        'views/membership_view.xml',
        'views/nutrition_view.xml',
        'wizard/membership_subscription.xml',
        'wizard/subscriber_schedules.xml',
        'views/subscriber_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'views/res_config_view.xml',
        'views/medical_views.xml',
        'report/report_gym_schedule_view.xml',
        'report/report_nutrition_schedule_view.xml',
        'report/reports.xml',
        'views/membership_portal_templates.xml',
        'views/gym_portal_templates.xml',
        'views/nutrition_portal_templates.xml',
        "static/src/xml/login_background.xml",
    ],
    'assets': {
        'web.assets_backend': [
            '/aspl_fitness_management/static/src/js/widgets/switch_branch_menu.js',
            '/aspl_fitness_management/static/src/js/branch_service.js',
            '/aspl_fitness_management/static/src/css/fitness_dashboard.css',
            '/aspl_fitness_management/static/src/js/Chart.js',
            '/aspl_fitness_management/static/src/js/fitness_dashboard.js',
            '/aspl_fitness_management/static/src/xml/base.xml',
            '/aspl_fitness_management/static/src/xml/fitness_dashboard.xml',
            '/aspl_fitness_management/static/src/css/login_background.css',
            '/aspl_fitness_management/static/src/css/multi_branch_widget.css',
        ],
        'web._assets_common_scripts': [
            # '/aspl_fitness_management/static/src/js/session.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
