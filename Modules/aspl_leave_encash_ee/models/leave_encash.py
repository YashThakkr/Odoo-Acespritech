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

from odoo import api, fields, models, _
from datetime import datetime
import warnings


class LeaveEncash(models.Model):
    _name = 'leave.encash'
    _description = 'Leave Encash'
    _rec_name = "employee_id"
    _order = 'id desc'

    employee_id = fields.Many2one("hr.employee", string="Employee")
    department_id = fields.Many2one("hr.department", string="Department")
    job_id = fields.Many2one("hr.job", string="Job Position")
    leave_carry = fields.Float(string="Leave Carry")
    date = fields.Datetime(string="Date", default=datetime.now())
    amount = fields.Float(string="Amount")
    leave_type_id = fields.Many2one("hr.leave.type", string="Leave Type")
    state = fields.Selection([('draft', 'Draft'),
                              ('approved', 'Approved'),
                              ('paid', 'Paid'),
                              ('canceled', 'Cancelled')], default='draft')
    payslip_id = fields.Many2one("hr.payslip", string="Payslip")

    def approve(self):
        self.state = 'approved'

    def cancel(self):
        self.state = 'canceled'

    def unlink(self):
        for each in self:
            if each.state == 'paid':
                warnings.warn(
                            "You cannot delete Paid records",
                            DeprecationWarning,
                            stacklevel=2
                        )
        return super(LeaveEncash, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
