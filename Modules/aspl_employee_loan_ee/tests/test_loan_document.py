from datetime import datetime

from odoo.tests.common import TransactionCase
from odoo import fields
import logging

_logger = logging.getLogger(__name__)


class TestLoanDocCategSettings(TransactionCase):

    def setUp(self):
        super().setUp()

    def test_all(self):
        test_result = {
            'name': 'Loan application flow',
            'errors': [],
            'succeed': [],
            'test_count': 0,
            'pass_count': 0,
            'fail_count': 0,
            'state': 'pass'
        }

        test_result['test_count'] += 1
        try:
            employee = self.env['hr.employee'].create({'name': 'Himani Parmar'})
            _logger.info("\n\n\n\nemployee===========================%s", employee)
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result.get('succeed').append(
                'employee created')
        except Exception as e:
            test_result['errors'].append(f'Failed to create employee: {str(e)}')
            test_result['fail_count'] += 1


        test_result['test_count'] += 1
        try:
            document = self.env['loan.document'].create({'name': 'Passport'})
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result.get('succeed').append(
                'loan document created')
            _logger.info("\n\n\n\ndocument===========================%s", document)
        except Exception as e:
            test_result['errors'].append(f'Failed to create loan document: {str(e)}')
            test_result['fail_count'] += 1


        test_result['test_count'] += 1
        try:
            applicant_category = self.env['applicant.category'].create({
                'name': 'Employee',
                'loan_doc_ids': [(6, 0, [document.id])]
            })
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result.get('succeed').append('applicant category created')

            _logger.info("\n\n\n\napplicant_category===========================%s", applicant_category)
        except Exception as e:
            test_result['errors'].append(f'Failed to create applicant category: {str(e)}')
            test_result['fail_count'] += 1


        test_result['test_count'] += 1
        try:
            loan_type = self.env['loan.type'].create({
                'name': 'Personal Loan',
                'minimum_amount': 100.0,
                'maximum_amount': 5000000.0,
                'minimum_term': 12,
                'maximum_term': 60,
                'fees_amount': 100,
                'method': 'reducing',
                'app_categ_ids': [(6, 0, [applicant_category.id])],
                'interest_rate': 5,
                'term_condition': 'Loan For employees only and should be paid in maximum 5 years'
            })
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result.get('succeed').append('loan_type created')
            _logger.info("\n\n\n\nloan_type===========================%s", loan_type)
        except Exception as e:
            test_result['errors'].append(f'Failed to create loan type: {str(e)}')
            test_result['fail_count'] += 1

        test_result['test_count'] += 1
        try:
            loan_settings = self.env['loan.setting'].create({
                'emp_loan_acc_id': 41,
                'bank_acc_id': 41,
                'interest_acc_id': 41,
                'loan_principal_acc_id': 41,
                'account_journal_id': 7,
                'service_charges_acc_id': 41,
                'other_fee_acc_id': 41,
                'installment_start_day': 1,
                'company_id': 1
            })
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result.get('succeed').append('loan_settings created')
            _logger.info("\n\n\n\nloan_settings===========================%s", loan_settings)
        except Exception as e:
            test_result['errors'].append(f'Failed to create loan settings: {str(e)}')
            test_result['fail_count'] += 1


        test_result['test_count'] += 1
        try:
            application_date = datetime.now()
            loan_application = self.env['loan.application'].create({
                'employee_id': employee.id,
                'template_id': 41,
                'loan_type_id': loan_type.id,
                'app_categ_id': applicant_category.id,
                'application_date': application_date,
                'requested_loan_amt': 1000,
                'service_charges': 1,
                'other_fee': 1,
                'rate_selection': 'floating',
                'loan_purpose': 'test loan',
            })
            loan_application.onchange_field()
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result.get('succeed').append('loan application created')
            _logger.info("\n\n\n\nloan_application.amount===========================%s", loan_application)
        except Exception as e:
            test_result['errors'].append(f'Failed to create loan application: {str(e)}')
            test_result['fail_count'] += 1


        try:
            for loan_id in loan_application.loan_type_doc_ids:
                loan_id.write({
                    'document': b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYGAAAAAEAAH2FzhVAAAAAElFTkSuQmCC'
                })
                test_result['test_count'] += 1

            for recs in loan_application.loan_type_doc_ids:
                recs.draft_to_verified()
                recs.verified_to_approved()
                test_result['test_count'] += 1

            if all(rec.state == 'approved' for rec in loan_application.loan_type_doc_ids):
                loan_application.approved_document()
                test_result.update({'pass_count': test_result.get('pass_count') + 1})
                test_result.get('succeed').append('loan application approved button called')
                test_result['test_count'] += 1
        except Exception as e:
            test_result['errors'].append(f'Failed during document upload or state change: {str(e)}')
            test_result['fail_count'] += 1


        try:
            loan_application.approved_loan_amt = 500.0
            loan_application.create_loan_calc()

            if loan_application.approved_loan_amt >= loan_type.minimum_amount:
                loan_application.verified_approve()

            if (loan_application.state != 'verified' and
                    loan_application.approved_loan_amt != 0.0 and
                    loan_application.approved_loan_amt <= loan_application.requested_loan_amt):
                loan_application.button_approved()
                test_result['test_count'] += 1

            loan_application.amount = loan_application.approved_loan_amt
            _logger.info("\n\n\n\nloan_application.amount===========================%s", loan_application.amount)
            wizard = self.env['loan.calc'].create({
                'loan_amount': loan_application.amount,
                'term': 12,
                'loan_type_id': loan_application.loan_type_id.id,
                'method': loan_type.method
            })
            _logger.info("\n\n\n\nwizard===========================%s", wizard)
            wizard.get_payment_data()
            loan_application.button_paid()
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result['succeed'].append('Loan Document and category Unit Test passed')
            test_result['test_count'] += 1
        except Exception as e:
            test_result['errors'].append(f'Failed during loan calculation or approval: {str(e)}')
            test_result['fail_count'] += 1


        test_result['test_count'] += 1
        try:
            payslip_rule = self.env['hr.salary.rule'].create({
                'name': 'Loan',
                'code': 'EMI',
                'category_id': self.env.ref('hr_payroll.DED').id,
                'amount_select': 'code',
                'amount_python_compute': """
result = 0.0
if payslip.loan_payment_ids:
    for loan in payslip.loan_payment_ids:
        result += loan.total * -1
else:
    result = 0.0
""",
                'struct_id': self.env.ref('hr_payroll.structure_002').id
            })
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result['succeed'].append('payslip rule created successfully')
            _logger.info("\n\n\n\npayslip rule===========================%s",payslip_rule)
        except Exception as e:
            test_result['errors'].append(f'Failed to create salary rule: {str(e)}')
            test_result['fail_count'] += 1


        test_result['test_count'] += 1
        try:
            employee_contract = self.env['hr.contract'].create({
                'name': 'Himani Parmar Contract',
                'employee_id': employee.id,
                'date_start': '2024-01-01',
                'wage': 50000,
                'structure_type_id': self.env.ref('hr_contract.structure_type_employee').id,
                'state': 'open',
            })
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result.update({'pass_count': test_result.get('pass_count') + 1})
            test_result['succeed'].append('employee_contract created successfully')
            _logger.info("\n\n\n\nemployee_contract===========================%s", employee_contract)
        except Exception as e:
            test_result['errors'].append(f'Failed to create employee contract: {str(e)}')
            test_result['fail_count'] += 1


        test_result['test_count'] += 1
        try:
            payslip_rec = self.env['hr.payslip'].create({
                'name': 'January Payslip',
                'employee_id': employee.id,
                'contract_id': employee_contract.id,
                'struct_id': self.env.ref('hr_payroll.structure_002').id,
                'date_from': '2024-01-01',
                'date_to': '2025-01-01',
            })
            _logger.info("\n\n\n\npayslip_rec===========================%s", payslip_rec)
            payslip_rec.compute_sheet()
            _logger.info("\n\n\n\npayslip_rec state===========================%s", payslip_rec.state)
            test_result['test_count'] += 1
            test_result['pass_count'] += 1
            payslip_rec.action_payslip_done()
            _logger.info("\n\n\n\npayslip_rec state==========================%s", payslip_rec.state)
            test_result['test_count'] += 1
            test_result['pass_count'] += 1
        except Exception as e:
            test_result['errors'].append(f'Failed to create or process payslip: {str(e)}')
            test_result['fail_count'] += 1


        _logger.info('\n\n\n\n========================Loan Document and category Unit Testing Finished with test result: %s', test_result)
        _logger.info('\n\n\n\n')




