import odoo
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from datetime import datetime, timedelta
from odoo.addons.web.controllers.main import Home, ensure_db, _get_login_redirect_url
from odoo.exceptions import AccessError, UserError, AccessDenied


# def _get_login_redirect_url(uid, redirect):
#     pass


class Home(http.Controller):
    def _login_redirect(self, uid, redirect=None):
        return _get_login_redirect_url(uid, redirect)

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        # ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if request.env.uid is None:
            if request.session.uid is None:
                # no user -> auth=public with specific website public user
                request.env["ir.http"]._auth_method_public()
            else:
                # auth=user
                request.update_env(user=request.session.uid)

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                values = {}
                user = request.env['res.users'].sudo().search([('id', '=', int(uid))])
                if user.has_group('aspl_direct_checkin.group_direct_checkin'):
                    employee_id = request.env['hr.employee'].sudo().search([('user_id','=', user.id)], limit=1)
                    if employee_id:
                        attendance_id = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee_id.id)], order='check_in desc', limit=1)
                        if attendance_id:
                            if attendance_id.check_out:
                                values.update({'login':'in', 'employee_name': employee_id.name,'employee_id':employee_id.id})
                                return request.render('aspl_direct_checkin.checkin_template', values)
                        else:
                            values.update({'login': 'in', 'employee_name': employee_id.name, 'employee_id':employee_id.id})
                            return request.render('aspl_direct_checkin.checkin_template', values)
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        # ensure_db()
        if not request.session.uid:
            return request.redirect('/web/login', 303)
        if kw.get('redirect'):
            return request.redirect(kw.get('redirect'), 303)

        request.update_env(user=request.session.uid)
        values = {}
        user = request.env['res.users'].sudo().search([('id', '=', int(request.uid))])
        if user.has_group('aspl_direct_checkin.group_direct_checkin'):
            employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            if employee_id:
                attendance_id = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee_id.id)],
                                                                           order='check_in desc', limit=1)
                if attendance_id:
                    if attendance_id.check_out:
                        values.update({'login': 'in', 'employee_name': employee_id.name, 'employee_id': employee_id.id})
                        return request.render('aspl_direct_checkin.checkin_template', values)
                else:
                    values.update(
                        {'login': 'in', 'employee_name': employee_id.name,
                         'employee_id': employee_id.id})
                    return request.render('aspl_direct_checkin.checkin_template',
                                          values)
        try:
            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return request.redirect('/web/login?error=access')

class DirectCheckinOut(http.Controller):

    @http.route('/direct/checkin', type='http', auth='public', methods=['POST'], csrf=False)
    def direct_checkinout(self, **kw):
        employee_id = request.env['hr.employee'].sudo().search([
            ('id', '=', kw.get('employee_id'))], limit=1)        
        if employee_id:
            if kw.get('attendance') == 'in':
                request.env['hr.attendance'].sudo().create({'employee_id': employee_id.id, 'check_in': datetime.now()})
        return request.redirect('/web?')

