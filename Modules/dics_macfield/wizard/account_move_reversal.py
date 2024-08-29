# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _

class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'

    reason = fields.Char(string='Reason',
                         compute='_compute_default_reason',
                         # default='_compute_default_reason'
                         readonly=False,
                         )

    @api.depends('move_ids.name')
    def _compute_default_reason(self):
        for reversal in self:
            if reversal.move_ids:
                references = []
                for packing in reversal.move_ids.line_ids.sale_line_ids.order_id.picking_ids:
                    references.append(packing.name)
                    print('=============', references)
                deliveries = _('Based on Deliveries: %s.') % ', '.join(references)
                a = "   "
                invoices = _('Based on AR Invoices: %(move_name)s.') % {'move_name': reversal.move_ids.name}
                reversal.reason = deliveries + a + invoices
                print('11111111111111', reversal.reason)


    def _prepare_default_reversal(self, move):
        reverse_date = self.date if self.date_mode == 'custom' else move.date
        return {
            'ref': self.reason,
            'remark': self.reason
            if self.reason
            else _('Reversal of: %s', move.name),
            'date': reverse_date,
            'invoice_date_due': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id.id,
            'invoice_payment_term_id': None,
            'invoice_user_id': move.invoice_user_id.id,
            'auto_post': 'at_date' if reverse_date > fields.Date.context_today(self) else 'no',
        }

