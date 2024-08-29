from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from datetime import datetime, timedelta, time
import datetime as datetime1
import logging
import odoo as odoo1
from odoo import SUPERUSER_ID, http, tools
from odoo.http import request

# import GeoIP
import pytz
import re
import json
import werkzeug
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
import os
from urllib.request import urlopen
from odoo.addons.web.controllers.home import Home as Homeweb
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url
from odoo.http import FilesystemSessionStore


def clear_session_history(u_sid, f_uid=False):
    """ Clear all the user session histories for a particular user """
    path = odoo1.tools.config.session_dir
    store = FilesystemSessionStore(
        path, session_class=odoo1.http.Session, renew_missing=True)
    session_fname = store.get_session_filename(u_sid)
    try:
        os.remove(session_fname)
        return True
    except OSError:
        pass
    return False


class Homeweb(Homeweb):

    @http.route()
    def web_login(self, redirect=None, **kw):
        should_redirect = "/restrict-clear-session-user"
        if redirect:
            should_redirect+="?redirect="+redirect
        redirect = should_redirect
        response = super(Homeweb, self).web_login(redirect,**kw)
        return response


    @http.route(['/restrict-clear-session-user',], type='http', auth="user", website=True)
    def restrict_clear_session_user(self, **post):
        redirect_url = post.get('redirect') or False
        redirect_url = _get_login_redirect_url(request.session.uid, redirect_url)
        id_session_new = request.session.sid
        if request.session.uid:
            user = request.env.user.sudo()
            if user.id_session:
                if user.id_session != id_session_new:
                    session_cleared = clear_session_history(user.id_session)
                    user.write({'id_session':id_session_new})
            else:
                user.write({'id_session':id_session_new})
        return request.redirect(redirect_url)



