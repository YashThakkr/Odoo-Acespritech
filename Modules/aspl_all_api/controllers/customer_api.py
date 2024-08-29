# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request, Response


class CustomerAPI(http.Controller):

    @http.route('/api/customers', type='http', auth='public', methods=['GET'], csrf=False)
    def get_customers(self, **kwargs):
       
        partners = request.env["res.partner"].sudo().search([('customer_rank', '>', 0)])

        partner_list = []
        for partner in partners:
            partner_list.append(
                {
                    "id": partner.id,
                    "name": partner.name,
                    "email": partner.email,
                }
            )

        response_data = {
            'status': 'success',
            "message": 'Get customers successfully',
            'data': partner_list,
        }
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/customers/<int:partner_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_customer(self, partner_id):
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not partner.exists():
            response_data = {
                'status': 'error',
                'message': 'customer not found',
                'data': []
            }

            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=404
            )

        response_data = {
            'status': 'success',
            'message': 'customer get successfully',
            'data': [{
                'id': partner.id,
                'name': partner.name,
                'email': partner.email,
                'phone': partner.phone,
            }] 
        }

        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/customers', type='http', auth='public', methods=['POST'], csrf=False)
    def create_customer(self, **kwargs):
        try:
            partner = request.env['res.partner'].sudo().create({
                'name': kwargs.get('name'),
                'email': kwargs.get('email'),
                'phone': kwargs.get('phone'),
            })
            response_data = {
                'status': 'success',
                "message": 'Partner created successfully.',
                'data': [{
                    'id': partner.id,
                    'name': partner.name,
                    'email': partner.email,
                    'phone': partner.phone,
                }]
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=201
            )
        except Exception as e:
            error_message = str(e)
            return Response(
                json.dumps({'error': 'partner creation failed', 'message': error_message}),
                content_type='application/json',
                status=400
            )

    @http.route('/api/customers/<int:partner_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_partner(self, partner_id, **kwargs):
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not partner.exists():
            response_data = {
                'status': 'error',
                'message': 'Partner not found',
                'data': []
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=404
            )

        partner.write({
            'name': kwargs.get('name'),
            'phone': kwargs.get('phone'),
        })

        response_data = {
            'status': 'success',
            'message': 'Customer updated successfully.',
            'data': [{
                'id': partner.id,
                'name': partner.name,
                'email': partner.email,
                'phone': partner.phone,
            }]  
        }
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )
