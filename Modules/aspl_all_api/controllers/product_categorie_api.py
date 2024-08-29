# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request, Response


class ProductCategoryAPI(http.Controller):

    @http.route('/api/product_categories', type='http', auth='public', methods=['GET'], csrf=False)
    def get_product_categories(self):
        # Fetch all product categories
        categories = request.env['product.category'].sudo().search([])
        category_list = []
        for category in categories:
            category_list.append({
                "id": category.id,
                "name": category.name,
                "parent_id": category.parent_id.id if category.parent_id else None,
                "child_ids": [child.id for child in category.child_id],
            })

        response_data = {
            'status': 'success',
            "message": 'Get all product categories successfully',
            'data': category_list
        }

        # Convert response data to JSON and return it with the correct headers
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/product_categories/<int:category_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_product_category(self, category_id):
        category = request.env['product.category'].sudo().browse(category_id)
        if not category.exists():
            return Response(
                json.dumps({'error': 'Product category not found'}),
                content_type='application/json',
                status=404
            )

        response_data = {
            'id': category.id,
            'name': category.name,
            'parent_id': category.parent_id.id if category.parent_id else None,
            'child_ids': [child.id for child in category.child_id],
        }
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/product_categories', type='http', auth='public', methods=['POST'], csrf=False)
    def create_product_category(self):
        try:
            # Access JSON payload
            data = json.loads(request.httprequest.data)

            # Extract category name and parent_id from the JSON payload
            name = data.get('name')
            parent_id = data.get('parent_id', None)

            if not name:
                return Response(
                    json.dumps({'error': 'Category name is required'}),
                    content_type='application/json',
                    status=400
                )

            # Create the product category
            category = request.env['product.category'].sudo().create({
                'name': name,
                'parent_id': parent_id,
            })

            response_data = {
                'id': category.id,
                'name': category.name,
                'parent_id': category.parent_id.id if category.parent_id else None,
                'child_ids': [child.id for child in category.child_id],
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=201
            )
        except Exception as e:
            error_message = str(e)
            return Response(
                json.dumps({'error': 'Product category creation failed', 'message': error_message}),
                content_type='application/json',
                status=400
            )

    @http.route('/api/product_categories/<int:category_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_product_category(self, category_id):
        category = request.env['product.category'].sudo().browse(category_id)
        if not category.exists():
            return Response(
                json.dumps({'error': 'Product category not found'}),
                content_type='application/json',
                status=404
            )

        try:
            # Access JSON payload
            data = json.loads(request.httprequest.data)

            # Update category name and parent_id from the JSON payload
            category.write({
                'name': data.get('name'),
                'parent_id': data.get('parent_id', None),
            })

            response_data = {
                'id': category.id,
                'name': category.name,
                'parent_id': category.parent_id.id if category.parent_id else None,
                'child_ids': [child.id for child in category.child_id],
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=200
            )
        except Exception as e:
            error_message = str(e)
            return Response(
                json.dumps({'error': 'Product category update failed', 'message': error_message}),
                content_type='application/json',
                status=400
            )