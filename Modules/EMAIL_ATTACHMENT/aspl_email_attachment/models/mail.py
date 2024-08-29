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

import base64
import unicodedata

import lxml
from odoo import models, tools,api


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    
    @api.depends('composition_mode', 'model', 'res_domain', 'res_ids', 'template_id')
    def _compute_attachment_ids(self):
        res = super(MailComposer, self)._compute_attachment_ids()
        if self.model and self.model in ['sale.order', 'account'] and self.res_ids:
            att_ids = self.env['ir.attachment'].search(
                [('res_model', '=', self.model), ('res_id', '=', eval(self.res_ids)[0])])
            attachment = self.env['ir.attachment']
            for att in att_ids:
                data_attach = {
                    'name': att.store_fname,
                    'datas': att.datas,
                    'store_fname': att.store_fname,
                    'res_model': 'mail.compose.message',
                    'res_id': 0,
                    'type': 'binary',
                    # override default_type from context, possibly meant for another model!
                }
                attachment |= attachment.create(data_attach)
            if attachment:
                attachment_id_list = self.attachment_ids.ids
                for attc_id in attachment:
                    attachment_id_list.append(attc_id.id)
                self.attachment_ids = attachment_id_list
        return res
    
    
    # ?? Old method which have supported in odoo 16
    # def _onchange_template_id(self, template_id, composition_mode, model, res_id):
       
    #     res = super(MailComposer, self)._onchange_template_id(template_id, composition_mode, model,
    #                                                           res_id)
    #     if model and model in ['sale.order', 'account'] and res_id:
    #         att_ids = self.env['ir.attachment'].search(
    #             [('res_model', '=', model), ('res_id', '=', res_id)])
    #         attachment = self.env['ir.attachment']
    #         for att in att_ids:
    #             data_attach = {
    #                 'name': att.store_fname,
    #                 'datas': att.datas,
    #                 'store_fname': att.store_fname,
    #                 'res_model': 'mail.compose.message',
    #                 'res_id': 0,
    #                 'type': 'binary',
    #                 # override default_type from context, possibly meant for another model!
    #             }
    #             attachment |= attachment.create(data_attach)
    #         if attachment:
    #             if res['value'].get('attachment_ids'):
    #                 for att in attachment:
    #                     res['value']['attachment_ids'][0][2].append(att.id)
    #             else:
    #                 res['value']['attachment_ids'] = attachment.ids
    #     return res


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_post_process_attachments(self, attachments, attachment_ids, message_data):
        return_values = {}
        ir_attachment = self.env['ir.attachment']
        email_attchment = self.env['ir.attachment']
        m2m_attachment_ids = []
        cid_mapping = {}
        fname_mapping = {}
        if attachment_ids:
            if not self._context.get('skip_attach'):
                filtered_attachment_ids = self.env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'mail.compose.message'),
                    ('create_uid', '=', self._uid),
                    ('id', 'in', attachment_ids)])
                if message_data['model'] in ['sale.order', 'account.move']:
                    model_attachment = self.env['ir.attachment'].sudo().search(
                        [('res_model', '=', message_data['model']),
                         ('res_id', '=', message_data['res_id'])])
                    for attachment in filtered_attachment_ids:
                        if not model_attachment.filtered(
                                lambda l: l.name == attachment.name and l.store_fname == attachment.store_fname):
                            email_attchment |= attachment
                    if email_attchment:
                        email_attchment.write(
                            {'res_model': message_data['model'], 'res_id': message_data['res_id']})
                else:
                    if filtered_attachment_ids:
                        filtered_attachment_ids.write(
                            {'res_model': message_data['model'], 'res_id': message_data['res_id']})
            m2m_attachment_ids += [(4, rec) for rec in attachment_ids]
        # Handle attachments parameter, that is a dictionary of attachments
        for attachment in attachments:
            cid = False
            if len(attachment) == 2:
                name, content = attachment
            elif len(attachment) == 3:
                name, content, info = attachment
                cid = info and info.get('cid')
            else:
                continue
            if isinstance(content, unicodedata):
                content = content.encode('utf-8')
            data_attach = {
                'name': name,
                'datas': base64.b64encode(str(content)),
                'type': 'binary',
                'datas_fname': name,
                'description': name,
                'res_model': message_data['model'],
                'res_id': message_data['res_id'],
            }
            new_attachment = ir_attachment.create(data_attach)
            m2m_attachment_ids.append((4, new_attachment.id))
            if cid:
                cid_mapping[cid] = new_attachment
            fname_mapping[name] = new_attachment
        if cid_mapping and message_data.get('body'):

            root = lxml.html.fromstring(tools.ustr(message_data['body']))
            postprocessed = False
            for node in root.iter('img'):
                if node.get('src', '').startswith('cid:'):
                    cid = node.get('src').split('cid:')[1]
                    attachment = cid_mapping.get(cid)
                    if not attachment:
                        attachment = fname_mapping.get(node.get('data-filename'), '')
                    if attachment:
                        node.set('src', '/web/image/%s' % attachment.id)
                        postprocessed = True
            if postprocessed:
                body = lxml.html.tostring(root, pretty_print=False, encoding='UTF-8')
                message_data['body'] = body
        return_values['attachment_ids'] = m2m_attachment_ids
        return return_values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
