# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
################################################################################

from odoo import models, fields, api


class ProfitabilityCustomerReportPdf(models.AbstractModel):
    _name = 'report.aspl_profitability_customer_report.profit_customer_temp'
    _description = "Report Profitability By Customer"

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'aspl_profitability_customer_report.profit_customer_temp')
        return {
            'doc_ids': self.env['profitability.customer.report'].browse(data['ids']),
            'doc_model': report.model,
            'docs': self,
            'data': data,
            'get_data': self.get_data,
            'get_total': self.get_total,
        }

    def get_total(self, sales, cogs):
        profitability = 0.0
        if sales or cogs:
            profitability = ((sales - cogs) / sales) * 100
        return profitability

    def _sql_query(self, obj):
        if not obj.customer_ids:
            partner_ids = self.env['res.partner'].search([('customer_rank', '>', 0)]).ids
        else:
            partner_ids = obj.customer_ids.ids
        if not obj.sale_team_ids:
            sale_team_ids = self.env['crm.team'].search([]).ids
        else:
            sale_team_ids = obj.sale_team_ids.ids
        if obj.is_show_credit:
            move_type = ['out_invoice', 'out_refund']
        else:
            move_type = ['out_invoice', '']

        SQL = """SELECT am.id as move_id,am.name as number, am.invoice_date AS date,am.move_type AS move_type,
                        rp.id AS partner_id,rp.name AS partner,rp.street AS street,rp.street2 AS street2,
                        rp.city AS city,rp.state_id AS state,rp.zip AS zip,rp.country_id AS country,aml.price_unit as sale,aml.quantity AS quantity,
		                (CASE WHEN am.move_type IN ('out_refund', 'in_refund') THEN -1 ELSE 1 END) * SUM(aml.price_unit * aml.quantity) AS sales,
                        ct.name AS team,ct.id AS team_id,pc.id AS category,pp.id AS product_id
                    FROM account_move_line AS aml
                    JOIN product_product pp ON pp.id = aml.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    JOIN product_category pc on pc.id = pt.categ_id
                    JOIN account_move am ON (am.id = aml.move_id)
                    JOIN res_partner rp ON (rp.id = am.partner_id)
                    JOIN crm_team ct ON (ct.id = rp.team_id)
                    WHERE rp.team_id in %s
                    AND rp.id in %s
                    AND am.move_type in %s
                    AND am.invoice_date <= '%s'
                    AND am.invoice_date >= '%s'
                    AND am.state = 'posted'
                    GROUP BY am.id,am.name,am.invoice_date,am.move_type,rp.id,rp.name,rp.street,rp.street2,rp.state_id,
                    rp.zip,rp.country_id,ct.name,ct.id,pc.id,pp.id,aml.price_unit,aml.quantity""" % (
            " (%s) " % ','.join(map(str, sale_team_ids)), " (%s) " % ','.join(map(str, partner_ids)),
            tuple(move_type), str(obj.to_date), str(obj.from_date))
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()

        for data in result:
            product = self.env['product.product'].browse(data.get('product_id'))
            sales = data.get('sales')
            cogs = -(product.standard_price * data.get('quantity')) if data.get('move_type') in ['out_refund',
                                                                                                 'in_refund'] else product.standard_price * data.get(
                'quantity')
            data.update({'sales': sales, 'cogs': cogs, 'profitability': ((sales - cogs) / sales) * 100})

        custom_team_detail = []
        for each_team in result:
            if each_team.get('team_id') not in [x.get('team_id') for x in custom_team_detail]:
                custom_team_detail.append(each_team)
            else:
                count = 0
                for custom_team in custom_team_detail:
                    if custom_team.get('team_id') == each_team.get('team_id') and custom_team.get(
                            'partner_id') == each_team.get('partner_id'):
                        sale = custom_team.get('sales') + each_team.get('sales')
                        cog = custom_team.get('cogs') + each_team.get('cogs')
                        custom_team.update(
                            {'sales': sale,
                             'cogs': cog,
                             'profitability': ((sale - cog) / sale) * 100})
                        count = count + 1

                if count == 0:
                    custom_team_detail.append(each_team)

        return custom_team_detail

    def get_data(self, obj):
        team_detail = self._sql_query(obj)
        final_dict = {}
        for key in team_detail:
            if key['team_id'] not in final_dict:
                final_dict.update({key['team_id']: [key]})
            else:
                final_dict[key['team_id']] += [key]
        return final_dict

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
