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

from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class CommissionPayment(models.Model):
    _name = 'commission.payment'
    _description = 'Agent Commission Payment'

    agent_id = fields.Many2one('res.partner', string='Agent', domain="[('is_agent', '=', True)]", required=True)
    commission_pay_ids = fields.One2many('agent.commission', 'payment_id', string='Commission Payment')
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())

    @api.onchange('agent_id')
    def _onchange_agent(self):
        data_filter = [('agent_id', '=', self.agent_id.id), ('state', '=', 'draft')]
        agent_commission_ids = self.env['agent.commission'].search(data_filter)
        self.commission_pay_ids = [(6, 0, agent_commission_ids.ids)]

    def payment(self):
        IrDefault = self.env['ir.config_parameter'].sudo()
        account_id = IrDefault.get_param('aspl_hotel.account_id')
        if not account_id:
            raise UserError(_(
                'Commission Account is not Found. Please go to Invoice Configuration and set the Commission account.'))
        else:
            account_id = self.env['account.account'].search([('id', '=', account_id)])
            if not account_id:
                raise UserError(_(
                    'Commission Account is not Found. Please go to Invoice Configuration and set the Commission account.'))
        agent_detail = {'partner_id': self.agent_id.id,
                        'invoice_date': date.today(),
                        'move_type': 'in_invoice'}
        invoice_line_data = []
        i = 1 if self.agent_id.commission_payment_type == 'monthly' \
            else 3 if self.agent_id.commission_payment_type == 'quarterly' \
            else 12
        self.agent_id.next_payment_date = date.today() + relativedelta(months=i)
        total_amount = 0
        for comission_pay in self.commission_pay_ids:
            total_amount += comission_pay.amount
            comission_pay.write({'state': 'reserved'})
            invoice_line_data.append((0, 0, {'account_id': account_id.id,
                                             'name': comission_pay.commission_number + " Agent Commission",
                                             'quantity': 1,
                                             'price_unit': comission_pay.amount,
                                             }
                                      ))
        agent_detail.update({'invoice_line_ids': invoice_line_data,
                             'vendor_commission_ids': [(6, 0, self.commission_pay_ids.ids)]
                            })
        invoice_id = self.env['account.move'].create(agent_detail)
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'bank')], limit=1)
        amount = total_amount * self.agent_id.currency_id._get_conversion_rate(
            from_currency=invoice_id.currency_id,
            to_currency=self.agent_id.currency_id,
            company=self.env.user.company_id, date=date.today())
        payment_id = self.env['account.payment'].create({'payment_type': 'outbound',
                                                         'partner_type': 'supplier',
                                                         'partner_id': self.agent_id.id,
                                                         'amount': amount,
                                                         'journal_id': journal_id.id,
                                                         'date': date.today(),
                                                         'payment_method_id': self.env.ref(
                                                            'account.account_payment_method_manual_in').id,
                                                         'ref': invoice_id.name})
        payment_id.action_post()
        for vendor_comission in invoice_id.vendor_commission_ids:
            if vendor_comission.state == 'reserved':
                vendor_comission.state = 'paid'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
