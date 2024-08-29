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
from datetime import datetime, date, timedelta


class WizardCRMInfo(models.TransientModel):
    _name = 'wizard.work.order'
    _description = "Wizard Work order"

    remark = fields.Char(string="Remark", required=True)

    @api.model_create_multi
    def create(self, vals):
        if self._context.get('default_work_order_id') and self._context.get('default_room_id'):
            domain = [('room_id.room_no', '=', self._context.get('default_room_id')),
                 ('work_order_id', '=', int(self._context.get('default_work_order_id'))),
                 ('status', '!=', 'done')]
            if self._context.get('default_task_name'):
                domain += [('work_order_categ_id.name', '=', self._context.get('default_task_name'))]
            order_line_id = self.env['work.order.line'].sudo().search(domain, limit=1)
            if order_line_id:
                diff = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                         '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(order_line_id.start_time),
                                                                                  '%Y-%m-%d %H:%M:%S')
                minutes = diff.seconds / 60
                order_line_id.write({'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                     'status': 'done',
                                     'work_duration': str(round(float(minutes), 2)),
                                     'remark': vals[0].get('remark')})
        return super(WizardCRMInfo, self).create(vals)

    def get_formview_id(self):
        return self.env.ref('aspl_hotel.wizard_work_order_form_view').id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
