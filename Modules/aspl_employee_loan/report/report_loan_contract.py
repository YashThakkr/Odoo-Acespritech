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

from odoo import api, models, _
from odoo.exceptions import ValidationError, RedirectWarning


class WrappedReportLoanContract(models.AbstractModel):
    _name = 'report.aspl_employee_loan.report_loan_contract'
    _description = 'report.aspl_employee_loan.report_loan_contract'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        loan_app_id = self.env['loan.application'].browse(docids)
        for loan_id in loan_app_id:
            if loan_id.amount == 0.0:
                raise ValidationError(_('You not allow to print the contract with zero loan amount'))
            if loan_id.state != 'paid':
                raise ValidationError(_("You can't print the contract before the loan is approved"))
        report = report_obj._get_report_from_name('aspl_employee_loan.report_loan_contract')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': loan_app_id,
            'get_offer_content': self.get_offer_content,
        }

        return docargs

    def get_offer_content(self, loan_id):
        result = ''
        if loan_id.template_id and loan_id.template_id.body_html:
            result = self.env['mail.render.mixin']._render_template(loan_id.template_id.body_html,
                                                                'loan.application', loan_id.ids)
        return result.get(1)
