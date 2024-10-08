{
    'name': 'Dics Import Invoice Bill',
    'version': '16.0.0.4',
    'description': " ",
    'author': 'DataInteger Consultancy Services LLP',
    'maintainer': 'DataInteger Consultancy Services LLP',
    'company': 'DataInteger Consultancy Services LLP',
    'website': 'https://www.datainteger.com',
    'license': 'OPL-1',
    'depends': ['sale_management','account','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_views.xml',
        #'views/partner_views.xml',
        'wizard/import_inv_view.xml',
        'wizard/not_imp_inv_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
