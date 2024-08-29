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


class AcesReportWizard(models.TransientModel):
    _name = 'aces.report.name'
    _rec_name = 'model_id'
    _description = 'Report Name'

    model_id = fields.Many2one('ir.model', string="Model", required=True)
    model = fields.Char(related="model_id.model", string="Model Name")
    reports_ids = fields.One2many('aces.report.line', 'report_name_id', string="Reports")

    _sql_constraints = [
        ('check_model_id_uniq', 'unique (model_id)', 'Model is Already exist')
    ]


class AcesReportLineWizard(models.TransientModel):
    _name = 'aces.report.line'
    _description = 'Report Line'

    report_name_id = fields.Many2one('aces.report.name', string="Model")
    report_id = fields.Many2one('ir.actions.report', string="Report", required=True)
    prefix = fields.Char(string="Prefix", required=True)
    suffix = fields.Char(string="Suffix")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
