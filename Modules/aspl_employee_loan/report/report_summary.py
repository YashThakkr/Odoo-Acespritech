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
from odoo.exceptions import ValidationError


class WrappedReportLoanSummary(models.AbstractModel):
    _name = 'report.aspl_employee_loan.report_loan_summary'
    _description = 'report.aspl_employee_loan.report_loan_summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        loan_app_id = self.env['loan.application'].browse(docids)
        for loan_id in loan_app_id:
            if loan_id.amount == 0.0:
                raise ValidationError(_('You not allow to print the summary with zero loan amount'))
            if loan_id.state != 'paid':
                raise ValidationError(_("You can't print the summary before the loan is approved"))
        report = report_obj._get_report_from_name('aspl_employee_loan.report_loan_contract')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': loan_app_id,
        }
        return docargs
