# -*- coding: utf-8 -*-
##############################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
##############################################################################
from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = "project.task"

    def get_projectview_action(self, task_id):
        view_id = self.env.ref('project.view_task_form2').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'current',
            'res_id': task_id,
        }

    @api.model
    def create(self, vals):
        res = super().create(vals)
        user_obj = self.env['res.users'].search([('id', '=', vals.get('user_ids')[0])])
        user_list = [[user.partner_id, 'update.list', {'render': True, 'create': True, 'name': res.create_uid.name, 'id': res.id}] for user in user_obj]
        self.env['bus.bus']._sendmany(user_list)
        return res

    def unlink(self):
        res = super().unlink()
        user_obj = self.env['res.users'].search([])
        user_list = [[user.partner_id, 'update.list', {'render': True}] for user in user_obj]
        self.env['bus.bus']._sendmany(user_list)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
