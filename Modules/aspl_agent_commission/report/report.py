"""
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
"""

from odoo import models, api


class AgentPaymentTemplate(models.AbstractModel):
    """
    Abstract class for Report template of payment
    """
    _name = 'report.aspl_agent_commission.agent_payment_template'
    _description = 'Agent Payment Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'aspl_agent_commission.agent_payment_template')

        return {
            'doc_ids': self.env['agent.commission.payment'].browse(data['ids']),
            'data': data,
            'datas': data['commission'],
            'doc_model': report.model,
            'docs': self,
        }
