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

from odoo import models, fields, api, _
from datetime import datetime, date


class ReportEmployeeOvertimeInv(models.AbstractModel):
    _name = 'report.aspl_hr_overtime.overtime_report_pdf'
    _description = "Report Employee Overtime Template"

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('aspl_hr_overtime.overtime_report_pdf')
        wizard = self.env["wizard.overtime"]
        docargs = {
            'doc_ids': self.env["wizard.overtime"].browse(docids[0]),
            'doc_model': report.model,
            'docs': self,
            'summary_data': wizard.summary_data,
            'overtime': wizard.overtime,
        }
        return docargs

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
