#-*- coding:utf-8 -*-
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
    'name': 'GBS Inventory',
    'category': 'GBS Inventory',
    'summary': 'GBS Inventory',
    'version': '17.0.1.0',
    'website': 'http://www.acespritech.com',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'description': "Inventory",
    'depends': [
        'base',
        'stock',
        'purchase'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'views/gbs_inventory_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: