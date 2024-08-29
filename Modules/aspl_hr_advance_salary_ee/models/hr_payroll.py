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

from odoo import api, fields, models, _


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'


    def action_payslip_done(self):
        super(hr_payslip, self).action_payslip_done()
        for rec in self:
            rec.compute_sheet()
            payment_id = self.env['salary.payment']
            sal_req_id = self.env['hr.advance.salary.request']
            for each in rec.salary_pay_ids:
                payment_ids = payment_id.search([('id', '=', each.id)])
                for each_id in payment_ids:
                    if not each_id.payslip_id:
                        each_id.update({'state': 'deducted', 'payslip_id': rec.id})
            adv_sal_req = []
            no_of_installment = 0
            for adv_sal_req_obj in rec.salary_pay_ids:
                # if adv_sal_req.adv_sal_req_id:
                adv_sal_req.append(adv_sal_req_obj.id)
                if adv_sal_req_obj.adv_sal_req_id.no_of_installment >= no_of_installment:
                    no_of_installment = adv_sal_req_obj.adv_sal_req_id.no_of_installment

            sal_payment_ids = payment_id.search_count([('state', '=', 'deducted'),
                                                       ('adv_sal_req_id', 'in', adv_sal_req)])
            # if sal_payment_ids == self.salary_pay_ids.adv_sal_req_id.no_of_installment:
            if sal_payment_ids == no_of_installment:
                for advance in rec.salary_pay_ids:
                    advance.adv_sal_req_id.update({'state': 'closed'})
            for adv_sal in rec.adv_sal_req_ids:
                adv_ids = sal_req_id.search([('id', '=', adv_sal.id)])
                for salary in adv_ids:
                    salary.update({'state': 'paid', 'payslip_id': rec.id})
            return rec.update({'state': 'done', 'paid': True})

    @api.depends('employee_id', 'date_from', 'date_to')
    def salary_cheque(self):
        for each in self:
            sal_payment_ids = each.env['salary.payment'].search([
                                                            ('state', '=', 'draft'),
                                                            ('adv_sal_req_id.employee_id', '=', each.employee_id.id),
                                                            ('date', '>=', each.date_from),
                                                            ('date', '<=', each.date_to),
                                                            ('adv_sal_req_id.state', '=', 'paid')])
            each.salary_pay_ids = sal_payment_ids

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_salary_next_sal(self):
        for each in self:
            adv_sal_req_ids = each.env['hr.advance.salary.request'].sudo().search([
                                                            ('state', '=', 'approved'),
                                                            ('employee_id', '=', each.employee_id.id),
                                                            ('payment_by', '=', 'next_salary'),
                                                            ('next_sal_date', '>=', each.date_from),
                                                            ('next_sal_date', '<=', each.date_to)])
            each.adv_sal_req_ids = adv_sal_req_ids

    salary_pay_ids = fields.One2many('salary.payment', 'adv_sal_req_id', compute="salary_cheque",
                                      string='Payment By')
    adv_sal_req_ids = fields.One2many('hr.advance.salary.request', 'payslip_id', compute='compute_salary_next_sal',
                                      string='Payment By', store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
