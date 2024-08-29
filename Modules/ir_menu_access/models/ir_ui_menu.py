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

from odoo import api, models
from odoo.http import request


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if args is None:
            args = []
        group_ids = self.env['res.groups'].sudo().search([('users', 'in', [self._uid])])
        ima_ids = self.env['ir.menu.access'].sudo().search([
            '|', ('group_ids', 'in', group_ids.ids),
            ('user_ids', 'in', [self._uid])]
        )
        if ima_ids:
            args += [('id', 'not in', ima_ids.menu_ids.ids)]
        self = self.sudo()
        return super(IrUiMenu, self).search(args, offset, limit,
                                            order, count=count)


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def webclient_rendering_context(self):
        if self._context.get('skip_access'):
            return {
                'menu_data': request.env['ir.ui.menu'].sudo().load_menus(request.session.debug),
                'session_info': self.session_info(),
            }
        else:
            return super(Http, self).webclient_rendering_context()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
