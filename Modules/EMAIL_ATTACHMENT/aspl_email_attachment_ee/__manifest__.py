# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
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
    'name': 'Odoo Email Attachment (Enterprise)',
    'version': '17.0.1.0.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'General',
    'description': """
        Module allows to send attachments in email.
    """,
    'website': 'http://www.acespritech.com',
    'price': 20,
    'currency': 'EUR',
    'summary': 'Module allows to send attachments in email.',
    'depends': ['base', 'mail', 'sale_management', 'account'],
    'data': ['views/mail_compose_message.xml',
             ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
