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

from odoo import api, models, fields


class ReportHotelWorkOrder(models.AbstractModel):
    _name = 'report.aspl_hotel.work_order_report'
    _description = "Report Hotel Work Order"

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        return {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': data.get('context').get('active_model'),
            'docs': self,
            'data': dict(data,get_data=self.get_data(data)),
        }

    def get_data(self, data):
        if data.get('form').get('user_id'):
            work_order_ids = self.env['work.order.detail'].search([('work_date', '>=', data['form']['start_date']),
                                                               ('work_date', '<=', data['form']['end_date']),
                                                               ('user_id', 'in', data.get('form').get('user_id'))])
        else:
            work_order_ids = self.env['work.order.detail'].search([('work_date', '>=', data['form']['start_date']),
                                                               ('work_date', '<=', data['form']['end_date']),
                                                               ])
        data_dict = {}
        for work_order in work_order_ids:
            if not work_order.work_date in data_dict:
                data_dict.update({work_order.work_date: {
                    work_order.user_id.name: [each_line for each_line in work_order.work_order_line_ids]}})
            else:
                if not work_order.user_id.name in data_dict[work_order.work_date].keys():
                    data_dict[work_order.work_date].update({
                        work_order.user_id.name: [each_line for each_line in work_order.work_order_line_ids]})
        return data_dict


class AgentPaymentTemplate(models.AbstractModel):
    _name = 'report.aspl_hotel.agent_payment_report_template'
    _description = 'Agent Payment Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not docids:
            docids = self.env['agent.commission.payment'].browse(self.env.context.get('active_ids'))
        return {
            'data': data['commission'],
            'doc_model': 'agent.commission.payment',
            'docs': docids,
            'docs_ids': docids.ids
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: