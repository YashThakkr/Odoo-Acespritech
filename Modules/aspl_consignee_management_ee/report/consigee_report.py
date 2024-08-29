#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models
from odoo import tools


class ConsigneeReport(models.Model):
    _name = "consignee.report"
    _description = "Consignee Transfer Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_category_id = fields.Many2one('product.category', string="Product Category")
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    to_partner_id = fields.Many2one('res.partner', 'To Partner', readonly=True)
    source_location_id = fields.Many2one('stock.location', 'Source Location', readonly=True)
    destination_location_id = fields.Many2one('stock.location', 'Destination Location',
                                              readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
    ], string='Status', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    is_return = fields.Boolean(string="Is Return", readonly=True)
    is_internal_transfer = fields.Boolean(string="Internal Transfer", readonly=True)
    name = fields.Char(string="Name", readonly=True)
    requested_qty = fields.Float(string="Requested Qty", readonly=True)
    transfer_qty = fields.Float(string="Transferred Qty", readonly=True)
    company_id = fields.Many2one('res.company', string="Company")

    def _select(self):
        select_str = """
            SELECT min(sctl.id) as id,
                   sctl.product_id AS product_id,
                   pc.id AS product_category_id,
                   sctl.uom_id AS uom_uom, 
                   res.id AS partner_id,
                   rest.id AS to_partner_id,
                   sum(sctl.transfer_qty) AS transfer_qty, 
                   sum(sctl.requested_qty) AS requested_qty,
                   sct.source_location_id AS source_location_id,
                   sct.destination_location_id AS destination_location_id,
                   sct.state AS state,
                   sct.date AS date,
                   sct.is_return AS is_return,
                   sct.is_internal_transfer AS is_internal_transfer,
                   sct.name AS name,
                   sct.company_id AS company_id
        """
        return select_str

    def _from(self):
        from_str = """
                stock_consignee_transfer_line sctl
                    LEFT JOIN stock_consignee_transfer sct ON sct.id=sctl.consignee_record_id
                    LEFT JOIN product_product pp ON pp.id=sctl.product_id
                    LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                    LEFT JOIN product_category pc ON pc.id=pt.categ_id
                    LEFT JOIN res_partner res ON res.id=sct.partner_id
                    LEFT JOIN res_partner rest ON rest.id=sct.to_partner_id
                    LEFT JOIN uom_uom u ON (u.id=sctl.uom_id)
                    LEFT JOIN stock_location sl ON (sl.id=sct.source_location_id)
                    LEFT JOIN stock_location sld ON (sld.id=sct.destination_location_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY 
                    sctl.product_id, 
                    sctl.uom_id, 
                    res.id, 
                    rest.id, 
                    sct.source_location_id, 
                    sct.destination_location_id, 
                    sct.state, 
                    sct.date, 
                    sct.is_return, 
                    sct.is_internal_transfer,
                    sct.name,
                    sct.company_id,
                    pc.id
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
