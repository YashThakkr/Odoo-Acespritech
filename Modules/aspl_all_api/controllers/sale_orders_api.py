# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request, Response


class SaleOrderAPI(http.Controller):

    @http.route('/api/sale_orders', type='http', auth='public', methods=['GET'], csrf=False)
    def get_sale_orders(self):
        # Fetch all sale orders
        orders = request.env['sale.order'].sudo().search([])
        order_list = []
        for order in orders:
            order_list.append({
                "id": order.id,
                "name": order.name,
                "partner_id": order.partner_id.id,
                "date_order": order.date_order.strftime('%Y-%m-%d %H:%M:%S') if order.date_order else None,
                "state": order.state,
                "order_line": [
                    {
                        "product_id": line.product_id.id,
                        "product_name": line.product_id.name,
                        "product_uom_qty": line.product_uom_qty,
                        "price_unit": line.price_unit,
                        "price_subtotal": line.price_subtotal,
                    }
                    for line in order.order_line
                ],
            })

        response_data = {
            'status': 'success',
            "message": 'Get all sale orders successfully',
            'data': order_list
        }

        # Convert response data to JSON and return it with the correct headers
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/sale_orders/<int:order_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_sale_order(self, order_id):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists():
            return Response(
                json.dumps({'error': 'Sale order not found'}),
                content_type='application/json',
                status=404
            )

        response_data = {
            'id': order.id,
            'name': order.name,
            'partner_id': order.partner_id.id,
            'date_order': order.date_order.strftime('%Y-%m-%d %H:%M:%S') if order.date_order else None,
            'state': order.state,
            'order_line': [
                {   
                    "id": line.id,
                    "product_id": line.product_id.id,
                    "product_name": line.product_id.name,
                    "product_uom_qty": line.product_uom_qty,
                    "price_unit": line.price_unit,
                    "price_subtotal": line.price_subtotal,
                }
                for line in order.order_line
            ],
        }
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=200
        )

    @http.route('/api/sale_orders', type='http', auth='public', methods=['POST'], csrf=False)
    def create_sale_order(self):
        try:
            # Access JSON payload
            data = json.loads(request.httprequest.data)

            # Extract sale order details from the JSON payload
            partner_id = data.get('partner_id')
            order_line_data = data.get('order_line', [])

            if not partner_id:
                return Response(
                    json.dumps({'error': 'Partner ID is required'}),
                    content_type='application/json',
                    status=400
                )

            # Create the sale order
            order = request.env['sale.order'].sudo().create({
                'partner_id': partner_id,
            })

            # Create the order lines
            for line in order_line_data:
                request.env['sale.order.line'].sudo().create({
                    'order_id': order.id,
                    'product_id': line['product_id'],
                    'product_uom_qty': line['product_uom_qty'],
                })

            response_data = {
                'status': 'success',
                'message': 'order create successfully',
                'data': [{
                    'id': order.id,
                    'name': order.name,
                    'partner_id': order.partner_id.id,
                    'date_order': order.date_order.strftime('%Y-%m-%d %H:%M:%S') if order.date_order else None,
                    'state': order.state,
                    'order_line': [
                        {
                            "product_id": line.product_id.id,
                            "product_name": line.product_id.name,
                            "product_uom_qty": line.product_uom_qty,
                            "price_unit": line.price_unit,
                            "price_subtotal": line.price_subtotal,
                        }
                        for line in order.order_line
                    ],
                }], 
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=201
            )
        except Exception as e:
            error_message = str(e)
            return Response(
                json.dumps({'error': 'Sale order creation failed', 'message': error_message}),
                content_type='application/json',
                status=400
            )

    @http.route('/api/sale_orders/<int:order_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_sale_order(self, order_id):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists():
            return Response(
                json.dumps({'error': 'Sale order not found'}),
                content_type='application/json',
                status=404
            )

        try:
            # Access JSON payload
            data = json.loads(request.httprequest.data)
            date_order = data.get('date_order')

            # Update sale order details from the JSON payload
            order.write({
                'partner_id': data.get('partner_id'),
                'date_order': date_order,
            })

            # Update order lines
            for line in data.get('order_line', []):
                if 'id' in line:
                    line_rec = request.env['sale.order.line'].sudo().browse(line['id'])
                    if line_rec.exists():
                        line_rec.write({
                            'product_id': line['product_id'],
                            'product_uom_qty': line['product_uom_qty'],
                            'price_unit': line['price_unit'],
                        })
                else:
                    request.env['sale.order.line'].sudo().create({
                        'order_id': order.id,
                        'product_id': line['product_id'],
                        'product_uom_qty': line['product_uom_qty'],
                        'price_unit': line['price_unit'],
                    })

            response_data = response_data = {
                'status': 'success',
                'message': 'order update successfully',
                'data': [{
                    'id': order.id,
                    'name': order.name,
                    'partner_id': order.partner_id.id,
                    'date_order': order.date_order.strftime('%Y-%m-%d %H:%M:%S') if order.date_order else None,
                    'state': order.state,
                    'order_line': [
                        {   
                            "id": line.id,
                            "product_id": line.product_id.id,
                            "product_name": line.product_id.name,
                            "product_uom_qty": line.product_uom_qty,
                            "price_unit": line.price_unit,
                            "price_subtotal": line.price_subtotal,
                        }
                        for line in order.order_line
                    ],
                }], 
            }
            return Response(
                json.dumps(response_data),
                content_type='application/json',
                status=200
            )
        except Exception as e:
            error_message = str(e)
            return Response(
                json.dumps({'error': 'Sale order update failed', 'message': error_message}),
                content_type='application/json',
                status=400
            )

    @http.route('/api/sale_orders/<int:order_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_sale_order(self, order_id):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists():
            return Response(
                json.dumps({'error': 'Sale order not found'}),
                content_type='application/json',
                status=404
            )
        
        if order.state == 'draft':
            order.unlink()
            return Response(
                json.dumps({'status': 'Sale order deleted'}),
                content_type='application/json',
                status=200
            )

        else:
            return Response(
                json.dumps(
                    {'error': 'You are delete order in draft state only.'}
                ),
                content_type='application/json',
                status=404
            )
