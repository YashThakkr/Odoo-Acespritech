# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request, Response


class ProductAttributeAPI(http.Controller):

    @http.route('/api/product_attributes', type='http', auth='public', methods=['GET'], csrf=False)
    def get_product_attributes(self):
        # Fetch all product attributes
        attributes = request.env['product.attribute'].sudo().search([])
        attribute_list = []
        for attribute in attributes:
            value_list = []
            for value in attribute.value_ids:
                value_list.append({
                    "id": value.id,
                    "name": value.name,
                })
            attribute_list.append({
                "id": attribute.id,
                "name": attribute.name,
                "values": value_list
            })

        response_data = {
            'status': 'success',
            "message": 'Get all product attributes successfully',
            'data': attribute_list
        }

        # Convert response data to JSON and return it with the correct headers
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/product_attributes/<int:attribute_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_product_attribute(self, attribute_id):
        attribute = request.env['product.attribute'].sudo().browse(attribute_id)
        if not attribute.exists():
            response_data = {
                'status': 'error',
                'message': 'Product attribute not found',
                'data': []
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=404
            )

        value_list = []
        for value in attribute.value_ids:
            value_list.append({
                "id": value.id,
                "name": value.name,
            })

        response_data = {
            'status': 'success',
            'message': 'Product attribute get successfully',
            'data': [{
                'id': attribute.id,
                'name': attribute.name,
                'values': value_list
            }]
        }
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/product_attributes', type='http', auth='public', methods=['POST'], csrf=False)
    def create_product_attribute(self, **kwargs):
        try:

            data = json.loads(request.httprequest.data)
            attribute = request.env['product.attribute'].sudo().create({
                'name': data.get('name'),
            })

            # Create the attribute values
            value_data = data.get('values', [])
            
            for value in value_data:
                request.env['product.attribute.value'].sudo().create({
                    'name': value['name'],
                    'attribute_id': attribute.id,
                })

            response_data = {
                'status': 'success',
                'message': 'Product attribute create successfully.',
                'data': [{
                    'id': attribute.id,
                    'name': attribute.name,
                    'values': [{'id': value.id, 'name': value.name} for value in attribute.value_ids],
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
                json.dumps({'error': 'Product attribute creation failed', 'message': error_message}),
                content_type='application/json',
                status=400
            )

    @http.route('/api/product_attributes/<int:attribute_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_product_attribute(self, attribute_id, **kwargs):
        attribute = request.env['product.attribute'].sudo().browse(attribute_id)
        if not attribute.exists():
            response_data = {
                'status': 'error',
                'message': 'Product attribute not found.',
                'data': []
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=404
            )

        try:
            data = json.loads(request.httprequest.data)
            attribute.write({
                'name': data.get('name'),
            })

            # Update or create attribute values
            value_data = data.get('values', [])
            for value in value_data:
                if 'id' in value:
                    value_rec = request.env['product.attribute.value'].sudo().browse(value['id'])
                    if value_rec.exists():
                        value_rec.write({
                            'name': value['name'],
                        })
                else:
                    request.env['product.attribute.value'].sudo().create({
                        'name': value['name'],
                        'attribute_id': attribute.id,
                    })

            response_data = {
                'status': 'success',
                'message': 'Product attribute updated successfully',
                'data': [{
                    'id': attribute.id,
                    'name': attribute.name,
                    'values': [{'id': value.id, 'name': value.name} for value in attribute.value_ids],
                }]
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=200
            )
        except Exception as e:
            error_message = str(e)
            return Response(
                json.dumps({'error': 'Product attribute update failed', 'message': error_message}),
                content_type='application/json',
                status=400
            )
