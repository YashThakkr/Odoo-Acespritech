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

try:
    import simplejson as json
except ImportError:
    import json
import urllib
import codecs
from odoo import tools


def geo_find(addr, key=''):
    # url = "https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key=AIzaSyAcB3rH5rvpdo4tBLkj29c4moM5lvGb2XA&address="
    url = "https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key="+key+"&address="

    url += urllib.parse.quote(addr.encode('utf8'))
    try:
        reader = codecs.getreader("utf-8")
        result = json.load(reader(urllib.request.urlopen(url)))
    except Exception as e:
        return False
    if result['status'] != 'OK':
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng'])

    except (KeyError, ValueError):
        return None


def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        country = '{1} {0}'.format(*country.split(',', 1))
    return tools.ustr(', '.join(filter(None, [street,
                                              ("%s %s" % (zip or '', city or '')).strip(),
                                              state,
                                              country])))


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    def _set_lat_long(self):
        for partner in self:
            if not partner:
                continue
            key = self.env['ir.config_parameter'].sudo().get_param('partner_search_map.google_api_key')
            if key:
                result = geo_find(geo_query_address(street=partner.street,
                                                    zip=partner.zip,
                                                    city=partner.city,
                                                    state=partner.state_id.name,
                                                    country=partner.country_id.name), key=key)
            else:
                result = geo_find(geo_query_address(street=partner.street,
                                                    zip=partner.zip,
                                                    city=partner.city,
                                                    state=partner.state_id.name,
                                                    country=partner.country_id.name), key='')
            print('\n\n result-----', result)
            if result:
                partner.latitude = result[0]
                partner.longitude = result[1]
            else:
                partner.latitude = ''
                partner.longitude = ''

    latitude = fields.Char(string="Geo Latitude", compute="_set_lat_long", store=True)
    longitude = fields.Char(string="Geo Longitude", compute="_set_lat_long", store=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_api_key = fields.Char(string='Google API KEY')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(google_api_key=self.env['ir.config_parameter'].sudo().get_param('partner_search_map.google_api_key'))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('partner_search_map.google_api_key', self.google_api_key)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
