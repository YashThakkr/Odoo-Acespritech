# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import Controller, request, route


class WebsiteSaleShippingDialogController(Controller):

    @route(
        '/aspl_website_delivery_address/display_shipping_address_dialog',
        type='json', auth='public', methods=['POST'], website=True,
    )
    def display_shipping_address_dialog(self, force_dialog=False, line_id=False, **kw):
        addresses = request.env['sale.order'].get_address(line_id)
        
        if not force_dialog:
            return False

        return request.env['ir.ui.view']._render_template(
            'aspl_website_delivery_address.shipping_dialog_modal',
            {
                'src': addresses,
            }
        )


    @route(
        '/aspl_website_delivery_address/shipping_address_data_dialog',
        type='json', auth='public', methods=['POST'], website=True,
    )
    def shipping_address_data_dialog(self, force_dialog=False, source=False, **kw):
        if not force_dialog:
            return False

        state_ids = request.env['res.country.state'].search_read(domain=[],fields=['id', 'name'])
        country_ids = request.env['res.country'].search_read(domain=[],fields=['id', 'name'])

        return request.env['ir.ui.view']._render_template(
            'aspl_website_delivery_address.shipping_address_data',
            {
                'state_ids': state_ids,
                'country_ids': country_ids,
                'source': source,
            }
        )