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
from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = 'Contact'

    @api.constrains('agent_commission_ids')
    def _check_commission_values(self):
        if self.agent_commission_ids.filtered(
                lambda line: line.calculation == 'percentage' and line.commission > 100 or line.commission < 0.0):
            raise UserError(_('Commission value for Percentage type must be between 0 to 100.'))

    birth_date = fields.Date(string="Birth Date")
    birth_county_id = fields.Many2one('res.country', string="Birth Country")
    birth_city = fields.Char(string="Birth City")
    guest_type = fields.Selection([('adult', 'Adult'), ('child', 'Child')], default='adult',
        string="Type")
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], default='m',
        string="Gender")
    vip_status_id = fields.Many2one('vip.status', string="VIP Status")
    payment_type_id = fields.Many2one('account.journal', string="Payment Method ")
    spouse_birth_date = fields.Date(string="Spouse Birth Date")
    wedding_anniversary = fields.Date(string="Wedding Anniversary")
    direct_billing_ac = fields.Selection([('test', 'Test'), ('testing', 'Testing')],
        string="Direct Billing A/C")
    is_agent = fields.Boolean(string="Agent")
    is_agency = fields.Boolean(string="Laundry Agency")
    is_transportation_agency = fields.Boolean(string="Transportation Agency")
    is_hotel_customer = fields.Boolean(string="Hotel Customer")
    # branch_id = fields.Many2one('company.branch', string="Branch",
    #                             default=lambda self: self.env.user.get_current_branch())
    agent_commission_ids = fields.One2many('res.partner.commission', 'partner_comm_id',
        'sale_order_id')
    commission_payment_type = fields.Selection([
        ('manually', 'Manually'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Commission Payment Type')
    next_payment_date = fields.Date(string='Next Payment Date', readonly=True, store=True)
    commission_count = fields.Float(string='Commission', compute='_compute_commission')
    booking_count = fields.Integer(string='Bookings', compute='_compute_booking')

    # @api.model
    # def search(self, args, offset=0, limit=None, order=None):
    #     user_rec = self.env['res.users'].sudo().browse(self._uid).branch_ids.ids
    #     if user_rec:
    #         sql = """SELECT id FROM res_partner
    #                     WHERE branch_id in %s""" % (" (%s) " % ','.join(map(str, user_rec)))
    #         self._cr.execute(sql)
    #         result = self._cr.fetchall()
    #         rec = [each[0] for each in result]
    #         args += ['|', ('id', 'in', rec), ('branch_id', '=', False)]
    #     return super(ResPartner, self).search(args, offset=offset, limit=limit,
    #                                           order=order)

    @api.constrains('is_agent')
    def check_vendor(self):
        if self.is_agent and self.customer_rank > 1:
            raise UserError(_('Supplier Must be Available When Agent Available'))

    def payment_cron(self):
        IrDefault = self.env['ir.config_parameter'].sudo()
        account_id = IrDefault.get_param('aspl_hotel.account_id')
        if account_id:
            account_id = self.env['account.account'].search([('id', '=', account_id)])
            if not account_id:
                raise UserError(_(
                    'Commission Account is not Found. Please go to Invoice Configuration and set the Commission account.'))
        agent_ids = self.search([('is_agent', '=', True),
                                    ('commission_payment_type', '!=', 'manually')])

        for agent in agent_ids:
            commission_ids = self.env['agent.commission'].search([('state', '=', 'draft'),
                                                                     ('agent_id', '=', agent.id)])
            if agent.next_payment_date == date.today() or not agent.next_payment_date:
                total_amount = 0
                agent_detail = {'partner_id': agent.id,
                                'invoice_date': date.today(),
                                'move_type': 'in_invoice', }
                vendor_commission_list, invoice_line_data = [], []
                for commission in commission_ids:
                    total_amount += commission.amount
                    i = 1 if agent.commission_payment_type == 'monthly' \
                        else 3 if agent.commission_payment_type == 'quarterly' \
                        else 12
                    agent.next_payment_date = date.today() + relativedelta(months=i)
                    commission.write({'state': 'reserved'})
                    vendor_commission_list.append(commission.id)
                    invoice_line_data.append((0, 0, {'account_id': account_id.id,
                                                     'name': commission.commission_number + " Agent Commission",
                                                     'quantity': 1,
                                                     'price_unit': commission.amount,
                                                     }
                                              ))
                    agent_detail.update({'invoice_line_ids': invoice_line_data,
                                         'vendor_commission_ids': [(6, 0, vendor_commission_list)]
                                         })

                invoice_id = self.env['account.move'].create(agent_detail)
                journal_id = self.env['account.journal'].search(
                    [('type', '=', 'bank')], limit=1)
                amount = total_amount * agent.currency_id._get_conversion_rate(
                    from_currency=invoice_id.currency_id,
                    to_currency=agent.currency_id, company=self.env.user.company_id,
                    date=date.today())

                payment_id = self.env['account.payment'].create({
                                                                 'payment_type': 'outbound',
                                                                 'partner_type': 'supplier',
                                                                 'partner_id': agent.id,
                                                                 'amount': amount,
                                                                 'journal_id': journal_id.id,
                                                                 'date': date.today(),
                                                                 'payment_method_id': '1',
                                                                 'ref': invoice_id.name})
                payment_id.action_post()
                for each in invoice_id.vendor_commission_ids:
                    if each.state == 'reserved':
                        each.state = 'paid'

    def _compute_commission(self):
        for customer in self:
            print("\n\n\n customer",customer)
            amount = 0
            commission_ids = self.env['agent.commission'].search([('agent_id', '=', self.id)])
            print("\n\n\n commission_ids",commission_ids)
            if not commission_ids:
                print("\n\n\n if not ---------- ")
                customer.commission_count = 0
            if customer.is_agent:
                print("\n\n\n if ------ ")
                for commission in commission_ids:
                    amount += commission.amount
                    print("\n\n\n amount", amount)
                customer.commission_count = amount
            else:
                customer.commission_count = 0

    def commission_payment_count(self):
        print("\n\n\n self commmission",self)
        return {
            'name': _('Agent Commission'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'agent.commission',
            'view_id': False,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'domain': [('agent_id', 'in', [self.id])],
        }

    def _compute_booking(self):
        for customer in self:
            customer.booking_count = self.env['walk.in.detail'].search_count(
                [('name', '=', customer.name)])

    def customer_booking_count(self):
        return {
            'name': _('Customer Booking'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'walk.in.detail',
            'view_id': False,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'domain': [('name', '=', self.name)],
        }


class ResPartnerCommission(models.Model):
    _name = 'res.partner.commission'
    _description = 'Agent Commission'

    agent_id = fields.Many2one('res.partner', string='Agent')
    calculation = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed_price', 'Fixed Price')
    ], string='Calculation')
    commission = fields.Float(string='Commission')
    # branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.get_current_branch())
    partner_comm_id = fields.Many2one('res.partner')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
