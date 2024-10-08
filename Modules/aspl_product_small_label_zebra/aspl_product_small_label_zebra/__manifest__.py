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
    'name': "Product Small Label with Zebra Printer (Community)",
    'version': '1.0',
    'category': 'Product',
    'description': """
        User can create custom label template by frontend and can print the dynamic product label report with Zebra Printer for Odoo which running in same premises or on cloud server.
    """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'summary': 'User can create custom label template by frontend and can print the dynamic product label report with Zebra Printer.',
    'depends': ['base', 'sale_management'],
    'price': 180,
    'currency': 'EUR',
    'data': [
         'views/aspl_product_small_label_zebra.xml',
         'views/prod_small_fields_label.xml',
         'views/wizard_product_small_label_report.xml',
         'data/design_data.xml',
         'views/printer_printer_view.xml',
         'views/printer_server.xml',
         'views/printer_job.xml',
         'views/label_config_settings_view.xml',
         'security/ir.model.access.csv',
         'report/aspl_product_small_label_zebra_report.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'external_dependencies':{
       'python':[
            'simple_zpl2', 'zebra', 'PIL', 'wand', 'pycups', 'cups'
       ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
            'web.assets_backend': [
                '/aspl_product_small_label_zebra/static/src/js/qweb_action_manager.js',
            ],
    },
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
