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
    "name": "Website Gift Voucher (Community)",
    "summary": "Website Gift Voucher",
    "version": "17.0.1.0",
    "description": """Gift Voucher""",
    "author": "Acespritech Solutions Pvt.Ltd.",
    "category": "Website",
    "website": "http://www.acespritech.com",
    "price": 25,
    "currency": "EUR",
    "depends": ["website_sale", "sale_management"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/sale_view.xml",
        "views/website.xml",
        "views/gift_voucher_detail_view.xml",
        "views/voucher_detail_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "aspl_website_gift_voucher/static/**/*",
        ],
    },
    "images": ["static/description/main_screenshot.png"],
    "license": "LGPL-3",
    "demo": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "application": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
