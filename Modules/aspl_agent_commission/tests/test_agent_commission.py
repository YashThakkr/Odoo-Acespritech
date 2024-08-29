from odoo.tests.common import TransactionCase
from odoo import fields
from odoo.tests import tagged
import logging

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestAgentCommission(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner1 = self.env['res.partner'].create({
            'name': 'Agent 1',
            'is_agent': True,
        })
        self.partner2 = self.env['res.partner'].create({
            'name': 'Test Customer'
        })
        _logger.info("\n\n\n\n partner===========================%s", self.partner1)
        self.assertTrue(self.partner1)
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
        })
        self.order = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': self.product.list_price,
            })]
        })

    # def test_agent(self):
    #     partner1 = self.env['res.partner'].create({
    #         'name': 'Agent 1',
    #         'is_agent': True,
    #     })
    #     partner2 = self.env['res.partner'].create({
    #         'name': 'Test Customer'
    #     })
    #     _logger.info("\n\n\n\n partner===========================%s", partner1)
    #     self.assertTrue(partner1)
    #     product = self.env['product.product'].create({
    #         'name': 'Test Product',
    #         'list_price': 100.0,
    #     })
    #     order = self.env['sale.order'].create({
    #         'partner_id': partner1.id,
    #         'order_line': [(0, 0, {
    #             'product_id': product.id,
    #             'product_uom_qty': 1,
    #             'price_unit': product.list_price,
    #         })]
    #     })

    def test_agent_confirmation(self):
        self.order.action_confirm()
        commission_id = self.env['agent.commission'].create({
            'order_id': self.order.id,
            'agent_id': self.partner1.id,
            'amount': 10.0,
        })
        commission_line = self.env['agent.commission'].search(
            [('order_id', '=', self.order.id), ('agent_id', '=', self.partner1.id)])
        _logger.info('\n\n\n\n commission_line-------%s', commission_line)

        self.assertTrue(commission_line, "Commission line should be created")

        expected_commission = 10.0
        self.assertEqual(commission_line.amount, expected_commission, "Commission amount should be 10.0")

    def test_agent_commission_payment(self):
        commission_line = self.env['agent.commission'].search(
            [('order_id', '=', self.order.id), ('agent_id', '=', self.partner1.id)])
        self.env['commission.payment'].create({
            'commission_pay_ids': commission_line,
            'agent_id': self.partner1.id,
        })

        payment = self.env['commission.payment'].search([('commission_pay_ids', '=', commission_line.id)])
        self.assertTrue(payment, "Commission payment should be created")
