"""
# -*- coding: utf-8 -*-
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
"""

from odoo import models, fields, api


# from odoo.addons.account.models.account_move import PAYMENT_STATE_SELECTION


class AgentCommission(models.Model):
    """Agent Commission class"""
    _name = 'agent.commission'
    _description = 'Agent Commission'

    agent_id = fields.Many2one('res.partner', string='Agent', required=True,
                               domain="[('is_agent', '=', True)]")
    name = fields.Char(string='Source Document')
    commission_date = fields.Date(string='Commission Date')
    amount = fields.Float(string='Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('billed', 'Bill Created'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft')
    payment_id = fields.Many2one('commission.payment', string='Payment')
    invoice_id = fields.Many2one('account.move')
    # payment_state = fields.Selection(selection=PAYMENT_STATE_SELECTION, string="Payment Status",tracking=True,
    #                                  compute='_compute_invoice_payment_state')
    payment_state = fields.Selection(
        selection=[
            ('not_paid', 'Not Paid'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
            ('partial', 'Partially Paid'),
            ('reversed', 'Reversed'),
            ('invoicing_legacy', 'Invoicing App Legacy'),
        ],
        string="Payment Status",
        compute='_compute_invoice_payment_state',
        tracking=True,
    )
    commission_number = fields.Char(string='Number')
    order_id = fields.Many2one('sale.order')

    def unlink(self):
        """
        Inheriting the unlink method for removing unwanted agent commission record 
        from commission payment wizard
        :return: unlinked record
        """
        
        if self._context.get('allow_delete') == False:
            rec = self.env['commission.payment'].search([('id','=',self.payment_id.id)])
            rec.write({'commission_pay_ids': [(2,rec.id)]})
        else:
            return super(AgentCommission, self).unlink()
    
    @api.model
    def create(self, vals):
        """
        Inheriting the create method for adding commission number
        :param vals: list of vals required for creation
        :return: newly created record
        """
        vals['commission_number'] = self.env['ir.sequence'].next_by_code('agent.commission.number')
        return super(AgentCommission, self).create(vals)

    def action_state(self):
        """
        Update the state of agent commission
        :return:
        """
        state = self._context.get('commission_state')
        vals = {'state': state}
        if state == 'cancel':
            vals['state'] = 'cancelled'
        elif state == 'reset':
            vals['state'] = 'draft'
        self.write(vals)

    @api.depends('invoice_id')
    def _compute_invoice_payment_state(self):
        for commission in self:
            if not commission.invoice_id:
                commission.write({'payment_state': 'not_paid'})
            if commission.invoice_id and commission.invoice_id.payment_state != 'paid':
                commission.write({'state': 'billed',
                                  'payment_state': commission.invoice_id.payment_state})
            elif commission.invoice_id and commission.invoice_id.payment_state == 'paid':
                commission.write({'state': 'paid',
                                  'payment_state': commission.invoice_id.payment_state})
            else:
                commission.write({'payment_state': 'not_paid'})
