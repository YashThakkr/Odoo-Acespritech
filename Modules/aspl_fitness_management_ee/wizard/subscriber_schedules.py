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

from odoo import models, fields, api
from odoo.exceptions import Warning


class SubscriberSchedule(models.TransientModel):
    _name = 'create.subscriber.schedule'
    _description = 'Create Subscriber Schedules'

    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    plan_id = fields.Many2one('gym.plan', string="Plan")
    gym_service_ids = fields.Many2many('product.product', 'subscriber_schedule_service_rel',
                                       'schedule_id',
                                       'service_id', string="Services")
    schedule_line_ids = fields.Many2many('schedule.line', string="Exercise Details")

    def button_create_schedules(self):
        # raise Warning('Have to Re-structure the code based on working schedule. '
        #               'Please Check the method!')
        lst = []
        subscriber_plan = self.env['subscriber.plan'].browse(self._context.get('active_id'))
        allowed_days = subscriber_plan.branch_id.resource_calendar_id.attendance_ids.mapped('dayofweek')
        for i in ['0', '1', '2', '3', '4', '5', '6']:
            if i in allowed_days:
                lst.append((0, 0, {
                    'plan_id': self.plan_id.id,
                    'day': i,
                    'line_ids': [(6, 0, self.schedule_line_ids.ids)],
                }))
        subscriber_plan.schedule_ids = lst

    @api.onchange('gym_service_ids')
    def onchange_exercises(self):
        service_lst = []
        self.schedule_line_ids = []
        for each in self.gym_service_ids:
            service_lst.extend([
                (0, 0, {'exercise_id': rec}) for rec in each.product_tmpl_id.exercise_ids.ids])
        self.schedule_line_ids = service_lst

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
