from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from datetime import datetime, timedelta, time
import datetime as datetime1
import logging
import odoo as odoo1
from odoo import SUPERUSER_ID
from odoo.http import request
# import GeoIP
import pytz
import re
import json
import os
from urllib.request import urlopen

_logger = logging.getLogger(__name__)



class ResUsers(models.Model):
    _inherit = 'res.users'

    session_ids = fields.One2many("restrict.users.session","user_id")
    id_session = fields.Char("Session ID")

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        session_obj = request.env['restrict.users.session']
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        user_obj = request.env['res.users']
        result = super(ResUsers, cls)._login(db, login, password, user_agent_env=user_agent_env)
        user_id = result
        user = user_obj.sudo().browse(user_id)
        url = 'http://ipinfo.io/'+str(ip)+'/json'
        response = urlopen(url)
        data = json.load(response)
        city = data.get('city') or False
        region=data.get('region') or False
        country=data.get('country') or False
        ip=data['ip']
        session_obj.sudo().create({'name':ip,'user_id':user.id,'city':city,'country':country,'region':region})
        if len(user.session_ids.ids) > 79:
            user.session_ids[0].unlink()

        return result

    

class RestrictUsersSession(models.Model):
    _name = 'restrict.users.session'
    _description = "Restrict Users Session"

    name = fields.Char("IP")
    city = fields.Char("City")
    country = fields.Char("Country Code")
    region = fields.Char("Region")
    user_id = fields.Many2one("res.users","Users")