from odoo import models, api, fields, _


class AccountMove(models.Model):
    _inherit = 'account.payment'

    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid'),
                                                    ('discount', 'Pay with discount')],
                                                   default='open', string="Payment Difference Handling", copy=False)
    discount_amount = fields.Monetary(string='Discount Amount', required=False, tracking=True)
    # discount_percentage = fields.Monetary(string='Discount Percentage', required=False, tracking=True)
    discount_percentage = fields.Float(string='Discount Percentage(%)', required=False, tracking=True)
    writeoff_label = fields.Char(
        string='Journal Item Label',
        help='Change label of the counterpart that will hold the payment difference',
        default=_('Write-Off'))
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    def get_discount(self, inv):
        return self.discount_amount

    def get_discount_percentage(self, inv):
        return self.discount_percentage

    def get_discount_amount(self, inv):
        discount = 0.0
        company = self.journal_id.company_id
        currency = self.currency_id or self.journal_id.currency_id or company.currency_id
        if self.outstanding_account_id:
            discount_line = self.env['account.move.line'].search(
                [('account_id', '=', self.outstanding_account_id.id), ('move_id', '=', self.move_id.id)])
            if discount_line:
                amount = discount_line.debit or discount_line.credit
                move_currency = discount_line.currency_id
                #     discount_amount = company.currency_id._convert(amount, currency, company, self.date)
                # else:
                #     discount_amount = amount
                if move_currency == currency and move_currency != company.currency_id:
                    discount_amount = company.currency_id._convert(amount, currency, company, self.date)
                else:
                    discount_amount = amount
                if move_currency == currency and move_currency != company.currency_id:
                    discount_amount = amount
                else:
                    discount_amount = company.currency_id._convert(amount, currency, company, self.date)
                if inv and move_currency:
                    invoice_currency = inv.currency_id
                    if move_currency == invoice_currency:
                        discount_amount = discount_line.amount_currency
                    elif invoice_currency == company.currency_id:
                        discount_amount = amount
                    else:
                        discount_amount = invoice_currency._convert(amount, move_currency, company, self.date)
                return discount_amount
        return discount

    def get_cash_amount(self, inv):
        ''' Function to get final received amount'''
        discount = self.get_discount_amount(inv)
        cash_amount = sum([
            data['amount']
            for data in inv.invoice_payments_widget['content']
            if data['account_payment_id'] == self.id
        ])
        return cash_amount - discount

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        write_off_line_vals = isinstance(write_off_line_vals, dict) and [write_off_line_vals]
        if not write_off_line_vals:
            return super()._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals,
                                                           force_balance=force_balance)
        for line_vals in write_off_line_vals:
            line_vals.update({'amount_currency': line_vals.pop('amount', 0.0),
                              'balance': line_vals.pop('balance', 0.0)})
        result = super()._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals,
                                                         force_balance=force_balance)
        for move_line in result:
            if self.analytic_account_id:
                move_line.update({
                    'analytic_account_id': self.analytic_account_id.id,
                })
        return result

    def action_post(self):
        result = super().action_post()
        for invoice_line in self.move_id.invoice_line_ids:
            if self.analytic_account_id:
                invoice_line.update({
                    'analytic_account_id': self.analytic_account_id.id
                })
        return result


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    payment_difference_handling = fields.Selection(
        selection_add=[('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid'),
                       ('discount', 'Pay with discount')],
        default='open', string="Payment Difference Handling", copy=False)
    discount_type = fields.Selection([('fix_amount', 'Fix Amount'), ('percentage', 'Percentage')],
                                     string="Discount Type", copy=False)
    discount_amount = fields.Monetary(string='Discount Amount', required=False, tracking=True)
    discount_percentage = fields.Float(string='Discount Percentage(%)', required=False, tracking=True)
    writeoff_label = fields.Char(
        string='Journal Item Label',
        help='Change label of the counterpart that will hold the payment difference',
        default=_('Write-Off'))

    @api.onchange('payment_difference_handling')
    def _onchange_payment_difference_handling(self):
        if self.payment_difference_handling == 'discount':
            discount_account = self.env['account.account'].search([('code', '=', '400001'),
                                                                   ('company_id', '=', self.company_id.id)], limit=1)
            if discount_account:
                self.writeoff_account_id = discount_account.id

    def get_discount_amount(self, inv):
        discount = 0.0
        company = self.journal_id.company_id
        currency = self.currency_id or self.journal_id.currency_id or company.currency_id
        if self.outstanding_account_id:
            discount_line = self.env['account.move.line'].search(
                [('account_id', '=', self.outstanding_account_id.id), ('move_id', '=', self.move_id.id)])
            if discount_line:
                amount = discount_line.debit or discount_line.credit
                move_currency = discount_line.currency_id
                # if currency != company.currency_id:
                #     discount_amount = company.currency_id._convert(amount, currency, company, self.date)
                # else:
                #     discount_amount = amount
                if move_currency == currency and move_currency != company.currency_id:
                    discount_amount = company.currency_id._convert(amount, currency, company, self.date)
                else:
                    discount_amount = amount
                if move_currency == currency and move_currency != company.currency_id:
                    discount_amount = amount
                else:
                    discount_amount = company.currency_id._convert(amount, currency, company, self.date)
                if inv and move_currency:
                    invoice_currency = inv.currency_id
                    if move_currency == invoice_currency:
                        discount_amount = discount_line.amount_currency
                    elif invoice_currency == company.currency_id:
                        discount_amount = amount
                    else:
                        discount_amount = invoice_currency._convert(amount, move_currency, company, self.date)
                return discount_amount
        return discount

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'currency_id': self.currency_id.id,
                'account_id': self.writeoff_account_id.id,
            }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'discount':
            if self.discount_type == 'fix_amount':
                discount = self.discount_amount
            else:
                discount = self.discount_percentage * self.payment_difference / 100
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': discount,
                'currency_id': self.currency_id.id,
                'account_id': self.writeoff_account_id.id,
            }
            payment_vals.update({'discount_amount': discount,
                                 'discount_percentage': self.discount_percentage})
        return payment_vals

    def _prepare_payment_moves(self):
        ''' Prepare the creation of journal entries (account.move) by creating a list of python dictionary to be passed
        to the 'create' method.

        Example 1: outbound with write-off:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |   900.0   |
        RECEIVABLE          |           |   1000.0
        WRITE-OFF ACCOUNT   |   100.0   |

        Example 2: internal transfer from BANK to CASH:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |           |   1000.0
        TRANSFER            |   1000.0  |
        CASH                |   1000.0  |
        TRANSFER            |           |   1000.0

        :return: A list of Python dictionary to be passed to env['account.move'].create.
        '''
        all_move_vals = []
        for payment in self:
            company_currency = payment.company_id.currency_id
            move_names = payment.move_name.split(
                payment._get_move_name_transfer_separator()) if payment.move_name else None

            # Compute amounts.
            write_off_amount = 0.0
            if payment.payment_difference_handling == 'reconcile':
                write_off_amount = -payment.payment_difference or 0.0
            elif payment.payment_difference_handling == 'discount':
                write_off_amount = -payment.discount_amount or 0.0
            if payment.payment_type in ('outbound', 'transfer'):
                counterpart_amount = payment.amount
                liquidity_line_account = payment.journal_id.default_debit_account_id
            else:
                counterpart_amount = -payment.amount
                liquidity_line_account = payment.journal_id.default_credit_account_id

            # Manage currency.
            if payment.currency_id == company_currency:
                # Single-currency.
                balance = counterpart_amount
                write_off_balance = write_off_amount
                counterpart_amount = write_off_amount = 0.0
                currency_id = False
            else:
                # Multi-currencies.
                balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
                                                       payment.date)
                write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id,
                                                                 payment.date)
                currency_id = payment.currency_id.id

            # Manage custom currency on journal for liquidity line.
            if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                # Custom currency on journal.
                if payment.journal_id.currency_id == company_currency:
                    # Single-currency
                    liquidity_line_currency_id = False
                else:
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                liquidity_amount = company_currency._convert(
                    balance, payment.journal_id.currency_id, payment.company_id, payment.date)
            else:
                # Use the payment currency.
                liquidity_line_currency_id = currency_id
                liquidity_amount = counterpart_amount

            # Compute 'name' to be used in receivable/payable line.
            rec_pay_line_name = ''
            if payment.payment_type == 'transfer':
                rec_pay_line_name = payment.name
            else:
                if payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Customer Payment")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Customer Credit Note")
                elif payment.partner_type == 'supplier':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Vendor Credit Note")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Vendor Payment")
                if payment.invoice_ids:
                    rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

            # Compute 'name' to be used in liquidity line.
            if payment.payment_type == 'transfer':
                liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
            else:
                liquidity_line_name = payment.name

            # ==== 'inbound' / 'outbound' ====

            move_vals = {
                'date': payment.date,
                'ref': payment.communication,
                'journal_id': payment.journal_id.id,
                'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                'partner_id': payment.partner_id.id,
                'line_ids': [
                    # Receivable / Payable / Transfer line.
                    (0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                        'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                        'date_maturity': payment.date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment.destination_account_id.id,
                        'payment_id': payment.id,
                    }),
                    # Liquidity line.
                    (0, 0, {
                        'name': liquidity_line_name,
                        'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                        'currency_id': liquidity_line_currency_id,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'date_maturity': payment.date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': liquidity_line_account.id,
                        'payment_id': payment.id,
                    }),
                ],
            }
            if write_off_balance:
                # Write-off line.
                move_vals['line_ids'].append((0, 0, {
                    'name': payment.writeoff_label,
                    'amount_currency': -write_off_amount,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'date_maturity': payment.date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': payment.outstanding_account_id.id,
                    'payment_id': payment.id,
                }))

            if move_names:
                move_vals['name'] = move_names[0]

            all_move_vals.append(move_vals)

            # ==== 'transfer' ====
            if payment.payment_type == 'transfer':
                journal = payment.destination_journal_id

                # Manage custom currency on journal for liquidity line.
                if journal.currency_id and payment.currency_id != journal.currency_id:
                    # Custom currency on journal.
                    liquidity_line_currency_id = journal.currency_id.id
                    transfer_amount = company_currency._convert(balance, journal.currency_id, payment.company_id,
                                                                payment.date)
                else:
                    # Use the payment currency.
                    liquidity_line_currency_id = currency_id
                    transfer_amount = counterpart_amount

                transfer_move_vals = {
                    'date': payment.date,
                    'ref': payment.communication,
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.destination_journal_id.id,
                    'line_ids': [
                        # Transfer debit line.
                        (0, 0, {
                            'name': payment.name,
                            'amount_currency': -counterpart_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.company_id.transfer_account_id.id,
                            'payment_id': payment.id,
                        }),
                        # Liquidity credit line.
                        (0, 0, {
                            'name': _('Transfer from %s') % payment.journal_id.name,
                            'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
                            'currency_id': liquidity_line_currency_id,
                            'debit': balance > 0.0 and balance or 0.0,
                            'credit': balance < 0.0 and -balance or 0.0,
                            'date_maturity': payment.date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.destination_journal_id.default_credit_account_id.id,
                            'payment_id': payment.id,
                        }),
                    ],
                }

                if move_names and len(move_names) == 2:
                    transfer_move_vals['name'] = move_names[1]

                all_move_vals.append(transfer_move_vals)
        return all_move_vals
