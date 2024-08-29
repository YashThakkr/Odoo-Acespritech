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
from odoo.exceptions import UserError
from odoo.exceptions import AccessDenied
import requests
import warnings


class PartnerSearchMap(models.TransientModel):
    _name = 'partner.search.map'
    _inherit = 'res.config.settings'
    _description = 'Partner Search Map'

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         obj = self.search([])
    #         if obj:
    #             obj[0].write(vals)
    #     return super().create(vals_list)

    company = fields.Boolean(string="Company", default=False)
    contact = fields.Boolean(string="Contact", default=False)
    name = fields.Char(string="Name")
    postcode = fields.Char(string="PostCode")
    city = fields.Char(string="City")
    state_id = fields.Many2one('res.country.state', string="State")
    country_id = fields.Many2one('res.country', string="Country")

    def show_map(self):
        try:
            check_connection = True
        except requests.ConnectionError:
            check_connection = False
        partner_obj = self.env['res.partner']
        print('\n\n\n\n\n\n partner_obj------', partner_obj)
        result = []
        company_domain = []
        contact_domain = []
        result.append({'connection': check_connection})
        print('\n result--', result)
        if not self.company and not self.contact:
            result.append({'no_data': 'Company and Contacts False'})
        if self.company:

            company_domain.append(('is_company', '=', True))
            if self.name:
                company_domain.append(('name', 'ilike', self.name))
            if self.postcode:
                company_domain.append(('zip', '=', self.postcode))
            if self.city:
                company_domain.append(('city', 'in', [self.city.lower(), self.city.upper(), self.city.capitalize()]))
            if self.state_id:
                company_domain.append(('state_id', '=', self.state_id.id))
            if self.country_id:
                company_domain.append(('country_id', '=', self.country_id.id))
            company_ids = partner_obj.search(company_domain)
            print('\n company_ids--', company_ids)
            for each_company in company_ids:
                if each_company.latitude and each_company.longitude:
                    result.append({'res_id': each_company.id,
                                   'name': each_company.name,
                                   'mobile': each_company.mobile,
                                   'street': each_company.street,
                                   'street2': each_company.street2,
                                   'city': each_company.city,
                                   'image': each_company.image_1920,
                                   'zip': each_company.zip,
                                   'state': each_company.state_id.name,
                                   'country': each_company.country_id.name,
                                   'latitude': each_company.latitude,
                                   'longitude': each_company.longitude})
        if self.contact:
            partner_ids = partner_obj.search([('is_company', '=', False)])
            if partner_ids:
                contact_domain.append(('id', 'in', partner_ids.ids))
                if self.name:
                    contact_domain.append(('name', 'ilike', self.name))
                if self.postcode:
                    contact_domain.append(('zip', '=', self.postcode))
                if self.city:
                    contact_domain.append(
                        ('city', 'in', [self.city.lower(), self.city.upper(), self.city.capitalize()]))
                if self.state_id:
                    contact_domain.append(('state_id', '=', self.state_id.id))
                if self.country_id:
                    contact_domain.append(('country_id', '=', self.country_id.id))
                contact_ids = partner_obj.search(contact_domain)
                for each_contact in contact_ids:
                    if each_contact.latitude and each_contact.longitude:
                        result.append({'res_id': each_contact.id,
                                       'name': each_contact.name,
                                       'mobile': each_contact.mobile,
                                       'street': each_contact.street,
                                       'street2': each_contact.street2,
                                       'city': each_contact.city,
                                       'image': each_contact.image_1920,
                                       'zip': each_contact.zip,
                                       'state': each_contact.state_id.name,
                                       'country': each_contact.country_id.name,
                                       'latitude': each_contact.latitude,
                                       'longitude': each_contact.longitude})
        print('\n\n----result', result)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
