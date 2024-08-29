# -*- coding: utf-8 -*-

{
    'name' : "Inventory Secondary Unit of Measure-UOM",
    "author": "Edge Technologies",
    'version': '16.0.1.1',
    'live_test_url': "https://youtu.be/hmzRJ-4WE0k",
    "images":['static/description/main_screenshot.png'],
    'summary': 'Inventory secondary unit of measure for inventory secondary unit of measure for warehouse secondary unit of measure product secondary UOM inventory secondary UOM for warehouse secondary UOM product secondary unit of measure for picking secondary UOM.',
    'description' : '''
           Inventory secondary unit of measure.
    
Secondary UOM
Stock in different UOMs
UOM
Unit of measure

    ''',
    "license" : "OPL-1",
    'depends' : ['stock'],
    'data': [
            'security/ir.model.access.csv',
            'security/secondary_uom_group.xml',
            'views/product_view.xml',
            'views/stock_move_view.xml',
            # 'views/stock_inventory_view.xml',
            'views/stock_quant_view.xml',
            'views/stock_scrap_view.xml',
            'views/inventory_report_template.xml',

             ],
    'installable': True,
    'auto_install': False,
    'price': 15,
    'currency': "EUR",
    'category': 'Warehouse',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
