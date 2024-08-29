from odoo import models, fields, api
import base64
import io
import xlwt


class HrSalarySheet(models.Model):
    _name = "aspl.salary.sheet"

    name = fields.Char(string='Name', required=True)
    date_to = fields.Date(string='Date To', required=True)
    state = fields.Selection([('paid', 'Paid'), ('unpaid', 'UnPaid'), ('partially_paid', 'Partially paid')])
    date_from = fields.Date(string='Date From', required=True)
    cheque_no = fields.Char(string='Cheque Number')
    total_to_pay = fields.Float(string='Total To Pay', compute='compute_salary_sheet', readonly=True)
    total_net_salary = fields.Float(string='Total Net Salary', compute='compute_salary_sheet', readonly=True)
    total_gross_salary = fields.Float(string='Total Gross Salary', compute='compute_salary_sheet', readonly=True)
    total_tax_deduction = fields.Float(string='Total Tax Deduction', readonly=True)
    total_advance = fields.Float(string='Total Advance', compute='compute_salary_sheet', readonly=True)
    payslip_ids = fields.One2many('aspl.hr.payslip', 'sheet_id', string='Payslips')
    file = fields.Binary(string='File Data')

    @api.onchange('date_to', 'date_from')
    def onchange_date(self):
        payslip_ids = self.env['hr.payslip'].search(
            [('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to), ('state', 'not in', ['cancel'])])
        for each in payslip_ids:
            self.payslip_ids = [(0, 0, {
                'payslip_id': each.id,
                'employee_id': each.employee_id,
                'basic_wage': each.basic_wage,
                'net_wage': each.net_wage,
                'payslip_run_id': each.payslip_run_id
            })]

    def compute_salary_sheet(self):
        for rec in self:
            payslip_ids = rec.env['hr.payslip'].search(
                [('date_from', '>=', rec.date_from), ('date_to', '<=', rec.date_to), ('state', 'not in', ['cancel'])])
            deduction = abs(
                sum(payslip_ids.mapped('line_ids').filtered(lambda x: x.category_id.code == 'DED').mapped('total')))
            total_to_pay = sum(
                payslip_ids.mapped('line_ids').filtered(lambda x: x.category_id.code == 'NET').mapped('total'))
            total_gross_salary = sum(
                payslip_ids.mapped('line_ids').filtered(lambda x: x.category_id.code == 'BASIC').mapped('total'))
            total_net_salary = sum(
                payslip_ids.mapped('line_ids').filtered(lambda x: x.category_id.code == 'GROSS').mapped(
                    'total')) - deduction
            total_advance = abs(
                sum(payslip_ids.mapped('line_ids').filtered(lambda x: x.salary_rule_id.code == 'EMI').mapped('total')))
            rec.total_to_pay = total_to_pay
            rec.total_gross_salary = total_gross_salary
            rec.total_net_salary = total_net_salary
            rec.total_advance = total_advance

    def action_salary_sheet(self):
        for rec in self:
            payslip_ids = rec.env['hr.payslip'].search(
                [('date_from', '>=', rec.date_from), ('date_to', '<=', rec.date_to), ('state', 'not in', ['cancel'])])
            total = sum(payslip_ids.mapped('line_ids').filtered(lambda x: x.category_id.code == 'NET').mapped('total'))

        workbook = xlwt.Workbook(encoding="UTF-8")
        worksheet = workbook.add_sheet('Salary Sheet')
        style = xlwt.easyxf(
            'font:height 200, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')
        style2 = xlwt.easyxf(
            'font:height 200, bold True, name Arial; align: horiz right;borders: top medium,right medium,bottom medium,left medium')
        style1 = xlwt.easyxf('align: horiz center')
        worksheet.write_merge(0, 1, 0, 4, self.env.company.name, style)
        worksheet.write_merge(2, 2, 0, 4, 'Salary Sheet of %s' % self.name, style)
        worksheet.write_merge(3, 3, 0, 4, 'Period', style)
        worksheet.write_merge(4, 4, 0, 1, 'Cheque Number', style)
        worksheet.write_merge(4, 4, 2, 4, '%s-%s' % (self.date_to, self.date_to), style)
        worksheet.write_merge(6, 6, 0, 4, 'Salary Details', style)
        worksheet.write(7, 0, 'No', style)
        worksheet.write(7, 1, 'Employee Name', style)
        worksheet.write(7, 2, 'Employee ID', style)
        worksheet.write(7, 3, 'Account Number', style)
        worksheet.write(7, 4, 'Amount', style)

        row = 8
        number = 0
        amount = 0
        for rec in payslip_ids:
            number += 1
            amount = rec.mapped('line_ids').filtered(lambda x: x.category_id.code == 'NET').total
            acc_number = rec.employee_id.bank_account_id.acc_number if rec.employee_id.bank_account_id else '-'
            symbol = self.env.company.currency_id.symbol
            worksheet.write(row, 0, number, style1)
            worksheet.write(row, 1, rec.employee_id.name)
            # worksheet.write(row, 2, rec.employee_id.id)
            worksheet.write(row, 3, acc_number, style1)
            worksheet.write(row, 4, "{} {:.2f}".format(symbol, amount), xlwt.easyxf('align: horiz right'))
            row += 1
        worksheet.write_merge(row, row, 0, 3, 'Total', style2)
        worksheet.write(row, 4, "{} {:.2f}".format(symbol, total), style2)

        fp = io.BytesIO()
        workbook.save(fp)
        self.write({
            'file': base64.encodebytes(fp.getvalue())
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/aspl.salary.sheet/%s/file/Salary Sheet %s-%s.xls?download=true' % (
            self.id, self.date_from, self.date_to),
            'target': 'self',
        }


class HrPayslip(models.Model):
    _name = "aspl.hr.payslip"

    payslip_id = fields.Many2one('hr.payslip', string='Payslip')
    sheet_id = fields.Many2one('aspl.salary.sheet')

    number = fields.Char(related='payslip_id.number')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee')
    state = fields.Selection([('paid', 'Paid'), ('unpaid', 'UnPaid'), ('partially_paid', 'Partially paid')])
    payslip_run_id = fields.Many2one(related='payslip_id.payslip_run_id')
    basic_wage = fields.Integer(string="Basic Wage")
    net_wage = fields.Integer(string="Net Wage")
    account_number = fields.Char(string="Account Number", related="employee_id.bank_account_id.acc_number")
    date_from = fields.Date(string="Date From", related="payslip_id.date_from")
    date_to = fields.Date(string="Date to", related="payslip_id.date_to")
    gross_salary = fields.Float(string="Gross Salary", compute='compute_sheet_salary')
    tax_deduction = fields.Float(string="Tax Deduction", compute='compute_sheet_salary')
    advance_deduction = fields.Float(string="Advance Deduction", compute='compute_sheet_salary')
    amount_to_pay = fields.Float(string="Amount To pay", compute='compute_sheet_salary')
    net_salary = fields.Float(string="Net Salary", compute='compute_sheet_salary')
    paid_amount = fields.Float(string="Paid Amount", compute='compute_sheet_salary')

    def compute_sheet_salary(self):
        for rec in self:
            payslip_ids = rec.env['hr.payslip'].search(
                [('date_from', '>=', rec.date_from), ('date_to', '<=', rec.date_to), ('state', 'not in', ['cancel']),
                 ('employee_id', '=', rec.employee_id.id), ('number', '=', rec.number)])
            gross_salary = sum(
                payslip_ids.mapped('line_ids').filtered(lambda x: x.category_id.code == 'BASIC').mapped('total'))
            tax_deduction = sum(
                payslip_ids.mapped('line_ids').filtered(lambda x: x.category_id.code == 'ADV').mapped('total'))
            advance_deduction = abs(
                sum(payslip_ids.mapped('line_ids').filtered(lambda x: x.salary_rule_id.code == 'EMI').mapped('total')))
            net_salary = sum(
                payslip_ids.mapped('line_ids').filtered(lambda x: x.category_id.code == 'GROSS').mapped(
                    'total')) - tax_deduction

            rec.gross_salary = gross_salary
            rec.tax_deduction = tax_deduction
            rec.advance_deduction = advance_deduction
            rec.net_salary = net_salary
            rec.paid_amount = payslip_ids.transfer_amount
            rec.amount_to_pay = rec.net_salary - rec.paid_amount

            if net_salary - rec.paid_amount == 0:
                rec.state = 'paid'
            elif rec.paid_amount == 0:
                rec.state = 'unpaid'
            elif rec.paid_amount != 0:
                rec.state = 'partially_paid'

