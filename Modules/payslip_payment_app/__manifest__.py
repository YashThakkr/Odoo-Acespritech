# -*- coding: utf-8 -*-

{
    "name" : "Payment for Employees Payslip",
    "author": "Edge Technologies",
    "version" : "16.0.1.1",
    "live_test_url":'https://youtu.be/r50lB3Ik_vI',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Employees payslip payment for payslip generate payment for payslip generate payment from payslip payment for salary slip create payment from salary slip payroll payment payroll payslip generate account payment from payroll account payment payroll payment',
    "description": """This odoo module helps to create payment 
                       payslip for all the users and users can 
                       see the different payment journal and this 
                       module also helps to create partial payments.
    """,
    "license" : "OPL-1",
    "depends" : ['base','hr','hr_payroll', 'account'],
    "data": [
        'security/ir.model.access.csv',
        'wizard/payslip_payment_wizard_view.xml',
        'views/hr_payslip_views.xml',
    ],
    "auto_install": False,
    "installable": True,
    "price": 10.0,
    "currency": 'EUR',
    "category" : "Human Resources",
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
