# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_round
from datetime import datetime
import operator as py_operator

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}



class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    secondary_uom_id = fields.Many2one('uom.uom', string="Secondary UOM")
    secondary_uom_name = fields.Char(string='Unit of Measure Name', related='secondary_uom_id.name', readonly=True)
    secondary_qty = fields.Float('Secondary Qty', compute='_compute_second_quantities', search='_search_second_qty_available',
        digits='Product Unit of Measure', compute_sudo=False)
    is_secondary_uom = fields.Boolean("Secondary Unit")


    @api.depends(
        'product_variant_ids',
        'product_variant_ids.stock_move_ids.product_qty',
        'product_variant_ids.stock_move_ids.state',
    )
    @api.depends_context('company')
    def _compute_second_quantities(self):
        res = self._compute_second_quantities_dict()
        for template in self:
            template.secondary_qty = res[template.id]['secondary_qty']
            template.update({'secondary_qty' : res[template.id]['secondary_qty']})

    def _is_cost_method_standard(self):
        return True

    def _compute_second_quantities_dict(self):
        # TDE FIXME: why not using directly the function fields ?
        variants_available = {
            p['id']: p for p in self.product_variant_ids.read(['secondary_qty'])
        }
        prod_available = {}
        for template in self:
            secondary_qty = 0
            for p in template.with_context(active_test=False).product_variant_ids:
                secondary_qty +=  p['secondary_qty']
            prod_available[template.id] = {
                "secondary_qty": secondary_qty
            }
        return prod_available

    def _search_second_qty_available(self, operator, value):
        domain = [('qty_available', operator, value)]
        product_variant_ids = self.env['product.product'].search(domain)
        return [('product_variant_ids', 'in', product_variant_ids.ids)]

    def action_open_secondary_quants(self):
        return self.with_context(active_test=False).product_variant_ids.filtered(lambda p: p.active or p.secondary_qty != 0).action_open_secondary_quants()


class Product(models.Model):
    _inherit = "product.product"

    secondary_qty = fields.Float(
        'Secondary Qty', compute='_compute_second_quantities', search='_search_second_qty_available',
        digits='Product Unit of Measure'
        , compute_sudo=False)

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    @api.depends_context(
        'lot_id', 'owner_id', 'package_id', 'from_date', 'to_date',
        'location', 'warehouse',
    )
    def _compute_second_quantities(self):
        products = self.filtered(lambda p: p.type != 'service')
        res = products._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        for product in products:
            product.secondary_qty = res[product.id]['secondary_qty']
        # Services need to be set with 0.0 for all quantities
        services = self - products
        services.secondary_qty = 0.0


    def _search_second_qty_available(self, operator, value):
        # In the very specific case we want to retrieve products with stock available, we only need
        # to use the quants, not the stock moves. Therefore, we bypass the usual
        # '_search_product_quantity' method and call '_search_qty_available_new' instead. This
        # allows better performances.
        if not ({'from_date', 'to_date'} & set(self.env.context.keys())):
            product_ids = self._search_qty_available_new(
                operator, value, self.env.context.get('lot_id'), self.env.context.get('owner_id'),
                self.env.context.get('package_id')
            )
            return [('id', 'in', product_ids)]
        return self._search_product_quantity(operator, value, 'secondary_qty')



    def _search_product_quantity(self, operator, value, field):
        # TDE FIXME: should probably clean the search methods
        # to prevent sql injections
        if field not in ('secondary_qty', 'qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty', 'free_qty'):
            raise UserError(_('Invalid domain left operand %s', field))
        if operator not in ('<', '>', '=', '!=', '<=', '>='):
            raise UserError(_('Invalid domain operator %s', operator))
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s', value))

        # TODO: Still optimization possible when searching virtual quantities
        ids = []
        # Order the search on `id` to prevent the default order on the product name which slows
        # down the search because of the join on the translation table to get the translated names.
        for product in self.with_context(prefetch_fields=False).search([], order='id'):
            if OPERATORS[operator](product[field], value):
                ids.append(product.id)
        return [('id', 'in', ids)]

    def _search_qty_available_new(self, operator, value, lot_id=False, owner_id=False, package_id=False):
        ''' Optimized method which doesn't search on stock.moves, only on stock.quants. '''
        product_ids = set()
        domain_quant = self._get_domain_locations()[0]
        if lot_id:
            domain_quant.append(('lot_id', '=', lot_id))
        if owner_id:
            domain_quant.append(('owner_id', '=', owner_id))
        if package_id:
            domain_quant.append(('package_id', '=', package_id))
        quants_groupby = self.env['stock.quant'].read_group(domain_quant, ['product_id', 'quantity','secondary_quantity'], ['product_id'], orderby='id')
        for quant in quants_groupby:
            if OPERATORS[operator](quant['quantity'], value):
                product_ids.add(quant['product_id'][0])
        return list(product_ids)

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            date_date_expected_domain_from = [('date', '>=', from_date)]
            domain_move_in += date_date_expected_domain_from
            domain_move_out += date_date_expected_domain_from
        if to_date:
            date_date_expected_domain_to = [('date', '<=', to_date)]
            domain_move_in += date_date_expected_domain_to
            domain_move_out += date_date_expected_domain_to

        Move = self.env['stock.move'].with_context(active_test=False)
        Quant = self.env['stock.quant'].with_context(active_test=False)
        domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in Quant.read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'], ['product_id'], orderby='id'))
        second_quants_res = dict((item['product_id'][0], (item['secondary_quantity'], item['quantity'])) for item in Quant.read_group(domain_quant, ['product_id', 'secondary_quantity', 'quantity'], ['product_id'], orderby='id'))
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            origin_product_id = product._origin.id
            product_id = product.id
            if not origin_product_id:
                res[product_id] = dict.fromkeys(
                    ['qty_available', 'free_qty', 'incoming_qty', 'outgoing_qty', 'virtual_available', 'secondary_qty'],
                    0.0,
                )
                continue
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(origin_product_id, [0.0])[0] - moves_in_res_past.get(origin_product_id, 0.0) + moves_out_res_past.get(origin_product_id, 0.0)
                second_qty_available = second_quants_res.get(origin_product_id, [0.0])[0] - moves_in_res_past.get(origin_product_id, 0.0) + moves_out_res_past.get(origin_product_id, 0.0)
            else:
                qty_available = quants_res.get(origin_product_id, [0.0])[0]
                second_qty_available = second_quants_res.get(origin_product_id, [0.0])[0]
            reserved_quantity = quants_res.get(origin_product_id, [False, 0.0])[1]
            res[product_id]['secondary_qty'] = float_round(second_qty_available, precision_rounding=rounding)
            res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
            res[product_id]['free_qty'] = float_round(qty_available - reserved_quantity, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(origin_product_id, 0.0), precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(origin_product_id, 0.0), precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                precision_rounding=rounding)

        return res

    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        return action

    def action_view_related_putaway_rules(self):
        self.ensure_one()
        domain = [
            '|',
                ('product_id', '=', self.id),
                ('category_id', '=', self.product_tmpl_id.categ_id.id),
        ]
        return self.env['product.template']._get_action_view_related_putaway_rules(domain)

    def action_open_product_lot(self):
        self.ensure_one()
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        action['context'] = {
            'default_product_id': self.id,
            'set_product_readonly': True,
            'default_company_id': (self.company_id or self.env.company).id,
        }
        return action

    # Be aware that the exact same function exists in product.template
    def action_open_quants(self):
        location_domain = self._get_domain_locations()[0]
        domain = expression.AND([[('product_id', 'in', self.ids)], location_domain])
        hide_location = not self.user_has_groups('stock.group_stock_multi_locations')
        hide_lot = all([product.tracking == 'none' for product in self])
        self = self.with_context(hide_location=hide_location, hide_lot=hide_lot)

        # If user have rights to write on quant, we define the view as editable.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_id=self.product_tmpl_id.id)
        ctx = dict(self.env.context)
        ctx.update({'no_at_date': True})
        return self.env['stock.quant'].with_context(ctx)._get_quants_action(domain)

    def action_update_quantity_on_hand(self):
        return self.product_tmpl_id.with_context(default_product_id=self.id).action_update_quantity_on_hand()

    def action_product_forecast_report(self):
        action = self.env.ref('stock.report_stock_quantity_action_product').read()[0]
        action['domain'] = [
            ('product_id', '=', self.id),
            ('warehouse_id', '!=', False),
        ]
        return action


    def action_open_secondary_quants(self):
        domain = [('product_id', 'in', self.ids)]
        hide_location = not self.user_has_groups('stock.group_stock_multi_locations')
        hide_lot = all(product.tracking == 'none' for product in self)
        self = self.with_context(
            hide_location=hide_location, hide_lot=hide_lot,
            no_at_date=True, search_default_on_hand=True,
        )

        # If user have rights to write on quant, we define the view as editable.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_id=self.product_tmpl_id.id)
        action = self.env['stock.quant']._get_quants_action(domain)
        action["name"] = _('Stock On Hand')
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4::