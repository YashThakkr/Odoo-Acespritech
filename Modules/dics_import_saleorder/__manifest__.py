{
    'name': 'Dics Import Sale Order',
    'version': '16.0.0.2',
    'description': " ",
    'author': 'DataInteger Consultancy Services LLP',
    'maintainer': 'DataInteger Consultancy Services LLP',
    'company': 'DataInteger Consultancy Services LLP',
    'website': 'https://www.datainteger.com',
    'license': 'OPL-1',
    'depends': ['sale_management', 'account', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizard/import_sale_order_view.xml',
        'wizard/not_imp_so_views.xml',

    ],
    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
