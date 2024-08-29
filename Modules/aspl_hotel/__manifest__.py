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
    'name': 'Hotel Management (Community)',
    'version': '1.0',
    'description': """
       Hotel Management System
    """,
    'author': 'Acespritech Solution Pvt. Ltd',
    'category': 'Industries',
    'website': 'https://www.acespritech.com',
    'images': [
        'static/description/hotel_management.png',
    ],
    'price': 500.00,
    'currency': 'EUR',
    'depends': ['base', 'sale_management', 'account', 'event', 'stock','fleet','payment',
                'sale_stock', 'purchase', 'web'],
    'data': [
        'data/data.xml',
        'data/ir_sequence_data.xml',
        'data/mail_template.xml',
        'report/hotel_laundry_report.xml',
        'report/agent_payment_report_template.xml',
        'report/account_invoice_report_view.xml',
        'report/purchase_report_views.xml',
        'report/sale_report_views.xml',
        'report/sale_report_templates.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menuitem.xml',
        'views/res_config_view.xml',
        'views/res_partner_view.xml',
        'views/hotel_view.xml',
        'views/hotel_room_view.xml',
        # 'views/template_js_css.xml',
        'views/house_keeping_view.xml',
        'views/hotel_laundry_view.xml',
        'views/hotel_folio_view.xml',
        'views/hotel_cancellation_policy.xml',
        'views/event_view.xml',
        'views/report.xml',
        'views/account_invoice_view.xml',
        'views/agent_commission_view.xml',
        'views/commission_analysis_view.xml',
        'views/commission_payment_view.xml',
        # 'views/branch_view.xml',
        'views/pick_drop.xml',
        'views/account_view.xml',
        'views/purchase_view.xml',
        'views/res_company_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'wizard/room_advance_payment_view.xml',
        'wizard/wizard_work_order_view.xml',
        'wizard/wizard_work_order_report.xml',
        'wizard/agent_commission_payment_view.xml',
        'wizard/account_report_common_view.xml',
    ],
    # 'qweb': ['static/src/xml/dashboard_data.xml',
    #         'static/src/xml/dashboard.xml',
    #         'static/src/xml/walk_in_calendar_view.xml',
    # ],
    'assets': {
        'web.assets_backend': [
            # 'aspl_hotel/static/src/css/dashboard.css',
            # 'aspl_hotel/static/src/css/fullcalendar.css',
            # 'aspl_hotel/static/src/css/scheduler.css',
            # 'aspl_hotel/static/src/css/scheduler.min.css',
            # 'aspl_hotel/static/src/css/walk_in_calendar.css',
            'aspl_hotel/static/src/js/dashboard.js',
            # 'aspl_hotel/static/src/js/lib/fullcalendar.js',
            # 'aspl_hotel/static/src/js/lib/scheduler.js',
            # 'aspl_hotel/static/src/js/walk_in_calendar.js',
            # 'aspl_hotel/static/src/js/widgets/switch_branch_menu.js',
            # 'aspl_hotel/static/src/js/branch_service.js',
            # 'aspl_hotel/static/src/xml/**/*',
            # 'aspl_hotel/static/src/xml/base.xml',
            'aspl_hotel/static/src/xml/dashboard_data.xml',
            'aspl_hotel/static/src/xml/dashboard.xml',
            # 'aspl_hotel/static/src/xml/walk_in_calendar_view.xml',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_check',
    'license' : 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
