# -*- coding: utf-8 -*-

from odoo import http, exceptions
from odoo.http import request, Response
import json


class AuthAPI(http.Controller):

    @http.route('/api/signup', type='http', auth='none', methods=['POST'], csrf=False)
    def signup(self):
        try:
            # Access JSON payload
            data = json.loads(request.httprequest.data)

            # Extract user details from the JSON payload
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            # Validate required fields
            if not name or not email or not password:
                return Response(
                    json.dumps({
                        'status': 'error',
                        'message': 'Name, email, password, and company_id are required'
                    }),
                    content_type='application/json',
                    status=400
                )

            # Check if the email is already registered
            existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if existing_user:
                return Response(
                    json.dumps({'status': 'error', 'message': 'Email is already registered'}),
                    content_type='application/json',
                    status=400
                )

            # Create new user
            new_user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'password': password,
                'company_id': 1,
                'company_ids': [(6, 0, [1])]  # Many2many relationship
            })

            # Prepare response data
            response_data = {
                'status': 'success',
                'message': 'New user created successfully',
                'data': {
                    'id': new_user.id,
                    'name': new_user.name,
                    'email': new_user.login,
                }
            }

            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=201
            )
        except exceptions.ValidationError as e:
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
                status=400
            )
        except Exception as e:
            return Response(
                json.dumps({'status': 'error', 'message': 'An unexpected error occurred', 'details': str(e)}),
                content_type='application/json',
                status=500
            )
