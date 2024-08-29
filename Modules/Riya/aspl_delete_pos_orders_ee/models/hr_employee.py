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
from odoo import api, fields, models


#For add access rights to field
class HrEmployeePin(models.Model):
    _inherit = "hr.employee"

    pin = fields.Char(string="PIN", groups="hr.group_hr_user,base.group_user", copy=False,
                      help="PIN used to Check In/Out in Kiosk Mode (if enabled in Configuration).")


class HrEmployeePublicPin(models.Model):
    _inherit = "hr.employee.public"

    pin = fields.Char(string="PIN",copy=False,
                      help="PIN used to Check In/Out.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
