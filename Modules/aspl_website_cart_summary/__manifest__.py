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
    "name": "Website Cart Summary (Community)",
    "version": "17.0.1.0.0",
    "category": "website",
    "summary": "website cart summary",
    "author": "Acespritech Solutions Pvt. Ltd.",
    "website": "http://www.acespritech.com",
    "images": ["static/description/main_screenshot.png"],
    "depends": ["website_sale"],
    "price": 25.00,
    "currency": "EUR",
    "data": [
        "views/website_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "aspl_website_cart_summary/static/**/*",
        ],
    },
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
