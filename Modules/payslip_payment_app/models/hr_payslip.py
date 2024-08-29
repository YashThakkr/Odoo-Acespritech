
from odoo import api, fields, models,_

class HrPayslip(models.Model):
	_inherit = "hr.payslip"

	state = fields.Selection(selection_add=([('paid', 'Paid')]))
	transfer_amount = fields.Float('Transfer Amount')

	def action_view_journal_entry(self):
		xml_id = 'account.view_move_tree'
		tree_view_id = self.env.ref(xml_id).id
		xml_id = 'account.view_move_form'
		form_view_id = self.env.ref(xml_id).id
		xml_id = 'account.view_account_move_kanban'
		kanban_view_id = self.env.ref(xml_id).id
		return {
			'name': _('Journal Entries'),
			'view_type': 'form',
			'view_mode': 'tree',
			'views': [(tree_view_id, 'tree'),(kanban_view_id, 'kanban'), 
					  (form_view_id, 'form')],
			'res_model': 'account.move',
			'domain': [('ref', 'ilike', self.number)],
			'type': 'ir.actions.act_window',
		}

	def check_transfer_amount(self):
		for record in self:
			line_ids = record.line_ids.filtered(lambda move: move.category_id.code == 'NET')
			if all(line.total == record.transfer_amount for line in line_ids):
				record.write({
					'state': 'paid',
				})
			else:
				record.write({
					'state': 'done',
				})