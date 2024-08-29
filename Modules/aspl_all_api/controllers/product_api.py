# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request, Response


class ProductAPI(http.Controller):
    
    @http.route('/api/products', type='http', auth='public', methods=['GET'], csrf=False)
    def get_products(self, **kwargs):
        print("################")
        # Default values for pagination
        page = int(kwargs.get('page', 1))
        page_size = int(kwargs.get('page_size', 10))

        # Calculate offset and limit for the SQL query
        offset = (page - 1) * page_size
        limit = page_size

        # Fetch the products with pagination
        products = request.env["product.product"].sudo().search([], offset=offset, limit=limit)
        total_products = request.env["product.product"].sudo().search_count([])

        product_list = []
        for product in products:
            product_list.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "price": product.lst_price,
                }
            )

        response_data = {
            'status': 'success',
            "message": 'Get products successfully',
            'data': product_list,
            'page': page,
            'page_size': page_size,
            'total': total_products,
            'total_pages': (total_products + page_size - 1) // page_size,  # Calculating total pages
        }

        # "http://<your-odoo-domain>/api/products?page=2&page_size=10"
        # Convert response data to JSON and return it with the correct headers
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/products/<int:product_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_product(self, product_id):
        product = request.env['product.product'].sudo().browse(product_id)
        if not product.exists():
            response_data = {
                'status': 'error',
                'message': 'Product not found',
                'data': []
            }

            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=404
            )

        response_data = {
            'id': product.id,
            'name': product.name,
            'price': product.lst_price,
        }
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/products', type='http', auth='public', methods=['POST'], csrf=False)
    def create_product(self, **kwargs):
        try:
            product = request.env['product.product'].sudo().create({
                'name': kwargs.get('name'),
                'lst_price': kwargs.get('price'),
            })
            response_data = {
                'status': 'success',
                "message": 'Product created successfully.',
                'data': [{
                    'id': product.id,
                    'name': product.name,
                    'price': product.lst_price,
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
                json.dumps({'error': 'Product creation failed', 'message': error_message}),
                content_type='application/json',
                status=400
            )

    @http.route('/api/products/<int:product_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_product(self, product_id, **kwargs):
        product = request.env['product.product'].sudo().browse(product_id)
        if not product.exists():
            response_data = {
                'status': 'error',
                'message': 'Product not found',
                'data': []
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=404
            )

        product.write({
            'name': kwargs.get('name'),
            'lst_price': kwargs.get('price'),
        })
        response_data = {
            'status': 'success',
            'message': 'Product updated successfully.',
            'data': [{
                'id': product.id,
                'name': product.name,
                'price': product.lst_price,
                'description': product.description,
            }]  
        }
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )
