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

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning


class PosDeleteOrder(models.TransientModel):
    _name = "pos.order.delete"
    _description = 'POS Order Delete'

    security_pin = fields.Char("Enter PIN")

    def delete_pos_order(self):
        user_id = self.env['res.users'].browse([self._uid])
        order_obj = self.env['pos.order']
        stock_picking_obj = self.env['stock.picking']
        if not user_id.allow_delete:
            error_msg = _('Sorry!\n'
                            'You are not allowed to perform this operation !')
            action_error = user_id._action_show()
            raise RedirectWarning(error_msg,action_error,_('Go to users'))
        if user_id.pin != self.security_pin:
            error_msg = _('Incorrect PIN!\n'
                            'Please Enter correct PIN!')
            action_error = user_id._action_show()
            raise RedirectWarning(error_msg,action_error,_('Go to users'))
        if self._context.get('active_ids'):
            orders = order_obj.browse(self._context.get('active_ids'))
            for order in orders:
                if order.state != 'paid':
                    error_msg = _('Incorrect Record!\n'
                                    'Records should be in paid state!')
                    action_error = order._action_show()
                    raise RedirectWarning(error_msg, action_error, _('Go to users'))

            # picking_ids = list(
            #     set([picking_id.id for order in orders for picking_id in order.picking_ids if order.picking_ids]))

            del_payment_line = ''' delete from pos_payment WHERE pos_order_id in %s''' % (
                    " (%s) " % ','.join(map(str, self._context.get('active_ids'))))
            self._cr.execute(del_payment_line)

            del_rec_line = ''' delete from pos_order WHERE id in %s''' % (
                    " (%s) " % ','.join(map(str, self._context.get('active_ids'))))
            self._cr.execute(del_rec_line)

            # return delivery orders
            pick_ids = stock_picking_obj.browse()

            for each in pick_ids:
                if each.state == 'assigned' or each.state == 'confirmed':
                    each.action_cancel()
                else:
                    return_picking_lst = []
                    for each_line in each.move_line_ids_without_package:
                        return_picking_lst.append(((0, 0, {
                            'product_id': each_line.product_id.id,
                            'uom_id': each_line.product_uom_id.id,
                            'quantity': each_line.qty_done,
                            'move_id': each_line.move_id.id,
                            'to_refund': True
                        })))
                    return_picking_id = self.env['stock.return.picking'].sudo().with_context(
                        return_picking_id=each.id).create({'product_return_moves': return_picking_lst,
                                                           'location_id': each.location_id.id,
                                                           'picking_id': each.id})

                    new_picking_id, pick_type_id = return_picking_id.sudo()._create_returns()
                    picking_id = stock_picking_obj.browse(new_picking_id)
                    wiz_id = self.env['confirm.stock.sms'].sudo().create({'pick_ids': [(4, picking_id.id)]})
                    if wiz_id:
                        wiz_id.send_sms()
                    wizard = self.env['stock.immediate.transfer'].sudo().with_context(
                        dict(self.env.context, default_show_transfers=False,
                             default_pick_ids=[(4, picking_id.id)])).create({})
                    wizard.process()
                    picking_id.sudo().button_validate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
