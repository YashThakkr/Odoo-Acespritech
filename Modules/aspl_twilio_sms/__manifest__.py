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
    'name': 'Twilio SMS (Community)',
    'category': 'Base',
    'version': '17.0.1.0.0',
    'license': 'LGPL-3',
    'price': 30.00,
    'currency': 'EUR',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'description': """Twilio SMS.""",
    'website': "http://www.acespritech.com",
    'summary': 'Send SMS with Twilio SMS Gateway',
    'depends': ['base_automation', 'sale_management', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_sms.xml',
        'wizard/wizard_connection_notification.xml',
        'views/sms_scheduler.xml',
        'views/send_sms.xml',
        'views/schedule_sms.xml',
        'views/sms_configuration.xml',
        'views/sale_view.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['twilio'],
    }
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
