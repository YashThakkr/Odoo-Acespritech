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
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class CommissionPayment(models.Model):
    """ Class for Commission Payment """
    _name = 'commission.payment'
    _description = 'Agent Commission Payment'

    agent_id = fields.Many2one('res.partner', string='Agent', domain="[('is_agent', '=', True)]",
                               required=True)
    commission_pay_ids = fields.One2many('agent.commission', 'payment_id',
                                         string='Commission Payment', context={'allow_delete': False})

    @api.onchange('agent_id')
    def _onchange_agent(self):
        """
        Handle the on change event for agent_id field
        :return:
        """
        data_filter = [('agent_id', '=', self.agent_id.id), ('state', '=', 'draft')]
        payment_browse = self.env['agent.commission'].search(data_filter)
        self.commission_pay_ids = [(6, 0, payment_browse.ids)]

    def payment(self):
        """
        Create payment for the res partner
        :return:
        """
        commission_account_id = self.env.user.company_id and self.env.user.company_id.commission_account_id
        if not commission_account_id:
            raise ValidationError(_(
                'Commission Account is not Found. Please go to related Company '
                'and set the Commission account.'))

        agent_detail = {'partner_id': self.agent_id.id,
                        'date': date.today(),
                        'invoice_date': date.today(),
                        'move_type': 'in_invoice'}
        invoice_line_data = []
        i = 1 if self.agent_id.commission_payment_type == 'monthly' \
            else 3 if self.agent_id.commission_payment_type == 'quarterly' \
            else 6 if self.agent_id.commission_payment_type == 'biyearly' \
            else 12
        self.agent_id.next_payment_date = date.today() + relativedelta(months=i)
        total_amount = 0
        
        if self.commission_pay_ids:
            for each in self.commission_pay_ids:
                total_amount += each.amount
                each.write({'state': 'billed'})
                invoice_line_data.append((0, 0, {'account_id': commission_account_id.id,
                                                'name': each.commission_number + " Agent Commission",
                                                'quantity': 1,
                                                'price_unit': each.amount,
                                                }))

            if self.agent_id.supplier_rank > 0:
                agent_detail.update({'invoice_line_ids': invoice_line_data,
                                    'agent_commission_ids': [(6, 0, self.commission_pay_ids.ids)]})
                invoice_id = self.env['account.move'].create(agent_detail)

                for each in invoice_id.agent_commission_ids:
                    each.payment_state = invoice_id.payment_state

                return {
                    'name': _('Bill created'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'view_id': self.env.ref('account.view_move_form').id,
                    'target': 'current',
                    'res_id': invoice_id.id,
                }
        else:
            raise ValidationError("Commission record is not found for this agent to generate bill. Please select another agent.")
