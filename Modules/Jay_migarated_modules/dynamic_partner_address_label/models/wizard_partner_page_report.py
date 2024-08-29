# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError

paper_format_dict = {'A0': [841, 1189], 'A1': [594, 841], 'A2': [420, 594], 'A3': [297, 420], 'A4': [210, 297],
                     'A5': [148, 210], 'A6': [105, 148], 'A7': [74, 105], 'A8': [52, 74], 'A9': [37, 52],
                     'B0': [1000, 1414], 'B1': [707, 1000], 'B2': [500, 707], 'B3': [353, 500], 'B4': [250, 353],
                     'B5': [176, 250], 'B6': [125, 176], 'B7': [88, 125], 'B8': [62, 88], 'B9': [33, 62], 'B10': [31, 44],
                     'C5E': [163, 229], 'Comm10E': [105, 241], 'DLE': [110, 220], 'Executive': [190.5, 254],
                     'Folio': [210, 330], 'Ledger': [431.8, 279.4], 'Legal': [215.9, 355.6], 'Letter': [215.9, 279.4],
                     'Tabloid': [279.4, 431.8]
}


class PartnerPageLabelDesign(models.Model):
    _name = 'partner.page.label.design'
    _description = 'Partner Page Lable Design'

    @api.model
    def default_get(self, fields_list):
        res = super(PartnerPageLabelDesign, self).default_get(fields_list)
        if self._context.get('wiz_id') and self._context.get('from_wizard'):
            for wiz in self.env['wizard.partner.page.report'].browse(self._context.get('wiz_id')):
                res.update({'page_template_design': wiz.column_report_design,
                            'report_model': wiz.report_model,
                            'page_width': wiz.page_width, 'page_height': wiz.page_height,
                            'dpi': wiz.dpi, 'margin_top': wiz.margin_top,
                            'margin_left': wiz.margin_left, 'margin_bottom': wiz.margin_bottom,
                            'margin_right': wiz.margin_right, 'orientation': wiz.orientation,
                            'humanReadable': wiz.humanReadable, 'barcode_height': wiz.barcode_height,
                            'barcode_width': wiz.barcode_width, 'display_height': wiz.display_height,
                            'display_width': wiz.display_width, 'with_barcode': wiz.with_barcode,
                            'format': wiz.format, 'col_no': wiz.col_no,
                            'col_width': wiz.col_width, 'col_height': wiz.col_height,
                            'label_logo': wiz.label_logo
                })
        return res

    name = fields.Char(string="Design Name")
    report_model = fields.Char(string='Model')
    page_template_design = fields.Text(string="Report Design")
    # page
    page_width = fields.Integer(string='Page Width (mm)', default=210)
    page_height = fields.Integer(string='Page Height (mm)', default=297)
    dpi = fields.Integer(string='DPI', default=80, help="The number of individual dots\
                                that can be placed in a line within the span of 1 inch (2.54 cm)")
    margin_top = fields.Float(string='Margin Top (mm)', default=1)
    margin_left = fields.Float(string='Margin Left (mm)', default=1)
    margin_bottom = fields.Float(string='Margin Bottom (mm)', default=1)
    margin_right = fields.Float(string='Margin Right (mm)', default=1)
    orientation = fields.Selection([('Landscape', 'Landscape'),
                                    ('Portrait', 'Portrait')],
                                   string='Orientation', default='Portrait', required=True)
    # barcode
    humanReadable = fields.Boolean(string="HumanReadable", help="User wants to print barcode number\
                                    with barcode page label.")
    barcode_height = fields.Integer(string="Height", default=300, required=True, help="This height will\
                                    required for the clearity of the barcode.")
    barcode_width = fields.Integer(string="Width", default=1500, required=True, help="This width will \
                                    required for the clearity of the barcode.")
    display_height = fields.Integer(string="Display Height (px)", required=True, default=40,
                                    help="This height will required for display barcode in page label.")
    display_width = fields.Integer(string="Display Width (px)", required=True, default=200,
                                    help="This width will required for display barcode in page label.")
    with_barcode = fields.Boolean(string='Barcode', help="Click this check box if user want to print\
                                    barcode for Partner Address Label.", default=True)
    # new columns and rows fields
    format = fields.Selection([('A0', 'A0  5   841 x 1189 mm'),
                                ('A1', 'A1  6   594 x 841 mm'),
                                ('A2', 'A2  7   420 x 594 mm'),
                                ('A3', 'A3  8   297 x 420 mm'),
                                ('A4', 'A4  0   210 x 297 mm, 8.26 x 11.69 inches'),
                                ('A5', 'A5  9   148 x 210 mm'),
                                ('A6', 'A6  10  105 x 148 mm'),
                                ('A7', 'A7  11  74 x 105 mm'),
                                ('A8', 'A8  12  52 x 74 mm'),
                                ('A9', 'A9  13  37 x 52 mm'),
                                ('B0', 'B0  14  1000 x 1414 mm'),
                                ('B1', 'B1  15  707 x 1000 mm'),
                                ('B2', 'B2  17  500 x 707 mm'),
                                ('B3', 'B3  18  353 x 500 mm'),
                                ('B4', 'B4  19  250 x 353 mm'),
                                ('B5', 'B5  1   176 x 250 mm, 6.93 x 9.84 inches'),
                                ('B6', 'B6  20  125 x 176 mm'),
                                ('B7', 'B7  21  88 x 125 mm'),
                                ('B8', 'B8  22  62 x 88 mm'),
                                ('B9', 'B9  23  33 x 62 mm'),
                                ('B10', ':B10    16  31 x 44 mm'),
                                ('C5E', 'C5E 24  163 x 229 mm'),
                                ('Comm10E', 'Comm10E 25  105 x 241 mm, U.S. '
                                 'Common 10 Envelope'),
                                ('DLE', 'DLE 26 110 x 220 mm'),
                                ('Executive', 'Executive 4   7.5 x 10 inches, '
                                 '190.5 x 254 mm'),
                                ('Folio', 'Folio 27  210 x 330 mm'),
                                ('Ledger', 'Ledger  28  431.8 x 279.4 mm'),
                                ('Legal', 'Legal    3   8.5 x 14 inches, '
                                 '215.9 x 355.6 mm'),
                                ('Letter', 'Letter 2 8.5 x 11 inches, '
                                 '215.9 x 279.4 mm'),
                                ('Tabloid', 'Tabloid 29 279.4 x 431.8 mm'),
                                ('custom', 'Custom')],
                               string='Paper Type', default="custom",
                               help="Select Proper Paper size")
    col_no = fields.Integer('No. of Column', default=1)
    col_width = fields.Float('Column Width (mm)', default=52.5)
    col_height = fields.Float('Column Height (mm)', default=29.7)
    from_col = fields.Integer(string="Start Column", default=1)
    from_row = fields.Integer(string="Start Row", default=1)
    active = fields.Boolean(string="Active", default=True)
    label_logo = fields.Binary(string="Label Logo")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_wizard') and self._context.get('report_model'):
            args.append(('report_model', '=', self._context.get('report_model')))
        elif self._context.get('from_wizard') and not self._context.get('report_model'):
            args.append(('report_model', '=', False))
        return super(PartnerPageLabelDesign, self).name_search(name, args=args, operator=operator, limit=limit)

    def close_wizard(self):
        self.write({'active': False})
        return {
            'name': _('Print Partner Address Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.partner.page.report',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }

    def go_to_label_wizard(self):
        if not self.name:
            raise UserError(_('Page Label Design Name is required.'))
        return {
            'name': _('Partner Address Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.partner.page.report',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }


class PartnerPageLabelQty(models.TransientModel):
    _name = 'partner.page.label.qty'
    _description = 'Partner Address Label Quantity'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    qty = fields.Integer(string='Quantity', default=1)
    partner_wiz_id = fields.Many2one('wizard.partner.page.report', string='Partner Wizard')
    line_id = fields.Integer(string='Line ID')


class WizardPartnerPageReport(models.TransientModel):
    _name = "wizard.partner.page.report"
    _description = 'Wizard Partner Page Report'

    @api.model
    def default_get(self, fields_list):
        partner_list_dict = []
        res = super(WizardPartnerPageReport, self).default_get(fields_list)

        if self._context.get('active_ids') and self._context.get('active_model') == 'purchase.order':
            partner_list_dict += [(0, 0, {'partner_id': po.partner_id.id, 'qty': 1, 'line_id': po.id}) \
                                    for po in self.env['purchase.order'].search([('id', 'in', self._context.get('active_ids'))]) if po.partner_id]

        elif self._context.get('active_ids') and self._context.get('active_model') == 'sale.order':
            partner_list_dict += [(0, 0, {'partner_id': so.partner_id.id, 'qty': 1, 'line_id': so.id}) \
                                    for so in self.env['sale.order'].search([('id', 'in', self._context.get('active_ids'))]) if so.partner_id]

        elif self._context.get('active_ids') and self._context.get('active_model') == 'stock.picking':
            partner_list_dict += [(0, 0, {'partner_id': sp.partner_id.id, 'qty': 1, 'line_id': sp.id}) \
                                    for sp in self.env['stock.picking'].search([('id', 'in', self._context.get('active_ids'))]) if sp.partner_id]

        elif self._context.get('active_ids') and self._context.get('active_model') == 'account.move':
            partner_list_dict += [(0, 0, {'partner_id': invoice.partner_id.id, 'qty': 1, 'line_id': invoice.id}) \
                                    for invoice in self.env['account.move'].search([('id', 'in', self._context.get('active_ids'))]) if invoice.partner_id]

        elif self._context.get('active_ids') and self._context.get('active_model') == 'res.partner':
            partner_list_dict += [(0, 0, {'partner_id': partner.id, 'qty': 1}) \
                                  for partner in self.env['res.partner'].search([('id', 'in', self._context.get('active_ids'))]) if partner]

        if self._context.get('active_model'):
            res['report_model'] = self._context.get('active_model')
            design_id = self.env['partner.page.label.design'].search([('report_model', '=', self._context.get('active_model'))], limit=1)
            if design_id:
                res['design_id'] = design_id.id
        else:
            res['report_model'] = 'wizard.partner.page.report'
            design_id = self.env['partner.page.label.design'].search([('report_model', '=', 'wizard.partner.page.report')], limit=1)
            if design_id:
                res['design_id'] = design_id.id
        res['partner_ids'] = partner_list_dict
        return res

    @api.model
    def _get_page_report_design(self):
        view_id = self.env['ir.ui.view'].search([('name', '=', 'dynamic_partner_page_rpt')])
        if view_id.arch:
            return view_id.arch

    @api.model
    def _get_page_report_id(self):
        view_id = self.env['ir.ui.view'].search([('name', '=', 'dynamic_partner_page_rpt')])
        if not view_id:
            raise UserError('Someone has deleted the reference view of report.\
                Please Update the module!')
        return view_id

    @api.model
    def _get_report_paperformat_id(self):
        xml_id = self.env['ir.actions.report'].search([('report_name', '=',
                                                        'dynamic_partner_address_label.dynamic_partner_page_rpt')])
        if not xml_id or not xml_id.paperformat_id:
            raise UserError('Someone has deleted the reference paper format of report.\
                Please Update the module!')
        return xml_id.paperformat_id.id

    @api.onchange('paper_format_id')
    def onchange_report_paperformat_id(self):
        if self.paper_format_id:
            self.format = self.paper_format_id.format
            self.page_width = self.paper_format_id.page_width
            self.page_height = self.paper_format_id.page_height
            self.orientation = self.paper_format_id.orientation
            self.margin_top = self.paper_format_id.margin_top
            self.margin_left = self.paper_format_id.margin_left
            self.margin_bottom = self.paper_format_id.margin_bottom
            self.margin_right = self.paper_format_id.margin_right
            self.dpi = self.paper_format_id.dpi

    @api.onchange('design_id')
    def on_change_design_id(self):
        if self.design_id:
            self.column_report_design = self.design_id.page_template_design
            self.report_model = self.design_id.report_model
            # paper format args
            self.format = self.design_id.format
            self.page_width = self.design_id.page_width
            self.page_height = self.design_id.page_height
            self.orientation = self.design_id.orientation
            self.dpi = self.design_id.dpi
            self.margin_top = self.design_id.margin_top
            self.margin_left = self.design_id.margin_left
            self.margin_bottom = self.design_id.margin_bottom
            self.margin_right = self.design_id.margin_right
            # barcode args
            self.with_barcode = self.design_id.with_barcode
            self.barcode_height = self.design_id.barcode_height
            self.barcode_width = self.design_id.barcode_width
            self.humanReadable = self.design_id.humanReadable
            self.display_height = self.design_id.display_height
            self.display_width = self.design_id.display_width
            # display row col args
            self.col_no = self.design_id.col_no
            self.col_width = self.design_id.col_width
            self.col_height = self.design_id.col_height
            self.label_logo = self.design_id.label_logo

    @api.onchange('dpi')
    def onchange_dpi(self):
        if self.dpi < 80:
            self.dpi = 80

    @api.onchange('col_width', 'col_height')
    def onchange_col_size(self):
        if self.col_height and self.col_width:
            if self.format != 'custom':
                format_size = paper_format_dict.get(self.format)
                if format_size:
                    total_col = format_size[0] / self.col_width
                    self.col_no = int(total_col)
                    self.col_no_float = total_col
            else:
                total_col = self.page_width / self.col_width
                self.col_no = int(total_col)
                self.col_no_float = total_col

    report_model = fields.Char(string="Model")
    design_id = fields.Many2one('partner.page.label.design', string="Template")
    partner_ids = fields.One2many('partner.page.label.qty', 'partner_wiz_id', string='Partner List')
    page_width = fields.Integer(string='Page Width (mm)', default=210)
    page_height = fields.Integer(string='Page Height (mm)', default=297)
    dpi = fields.Integer(string='DPI', default=80, help="The number of individual dots \
                        that can be placed in a line within the span of 1 inch (2.54 cm)")
    margin_top = fields.Float(string='Margin Top (mm)', default=1)
    margin_left = fields.Float(string='Margin Left (mm)', default=1)
    margin_bottom = fields.Float(string='Margin Bottom (mm)', default=1)
    margin_right = fields.Float(string='Margin Right (mm)', default=1)
    orientation = fields.Selection([('Landscape', 'Landscape'),
                                    ('Portrait', 'Portrait')],
                                   string='Orientation', default='Portrait', required=True)
    # barcode input
    humanReadable = fields.Boolean(string="HumanReadable", help="User wants to print barcode number \
                                    with barcode label.")
    barcode_height = fields.Integer(string="Height", default=300, required=True,
                                    help="This height will required for the clearity of the barcode.")
    barcode_width = fields.Integer(string="Width", default=1500, required=True,
                                   help="This width will required for the clearity of the barcode.")
    display_height = fields.Integer(string="Display Height (px)", required=True, default=40,
                                    help="This height will required for display barcode in page label.")
    display_width = fields.Integer(string="Display Width (px)", required=True, default=200,
                                   help="This width will required for display barcode in page label.")
    # report design
    view_id = fields.Many2one('ir.ui.view', string='Report View', default=_get_page_report_id)
    paper_format_id = fields.Many2one('report.paperformat', string="Paper Format", default=_get_report_paperformat_id)
    with_barcode = fields.Boolean(string='Barcode', help="Click this check box if user want to\
                        print barcode for Partner Address Label.", default=True)
    # new columns and rows fields
    format = fields.Selection([('A0', 'A0  5   841 x 1189 mm'),
                                ('A1', 'A1  6   594 x 841 mm'),
                                ('A2', 'A2  7   420 x 594 mm'),
                                ('A3', 'A3  8   297 x 420 mm'),
                                ('A4', 'A4  0   210 x 297 mm, 8.26 x 11.69 inches'),
                                ('A5', 'A5  9   148 x 210 mm'),
                                ('A6', 'A6  10  105 x 148 mm'),
                                ('A7', 'A7  11  74 x 105 mm'),
                                ('A8', 'A8  12  52 x 74 mm'),
                                ('A9', 'A9  13  37 x 52 mm'),
                                ('B0', 'B0  14  1000 x 1414 mm'),
                                ('B1', 'B1  15  707 x 1000 mm'),
                                ('B2', 'B2  17  500 x 707 mm'),
                                ('B3', 'B3  18  353 x 500 mm'),
                                ('B4', 'B4  19  250 x 353 mm'),
                                ('B5', 'B5  1   176 x 250 mm, 6.93 x 9.84 inches'),
                                ('B6', 'B6  20  125 x 176 mm'),
                                ('B7', 'B7  21  88 x 125 mm'),
                                ('B8', 'B8  22  62 x 88 mm'),
                                ('B9', 'B9  23  33 x 62 mm'),
                                ('B10', ':B10    16  31 x 44 mm'),
                                ('C5E', 'C5E 24  163 x 229 mm'),
                                ('Comm10E', 'Comm10E 25  105 x 241 mm, U.S. '
                                 'Common 10 Envelope'),
                                ('DLE', 'DLE 26 110 x 220 mm'),
                                ('Executive', 'Executive 4   7.5 x 10 inches, '
                                 '190.5 x 254 mm'),
                                ('Folio', 'Folio 27  210 x 330 mm'),
                                ('Ledger', 'Ledger  28  431.8 x 279.4 mm'),
                                ('Legal', 'Legal    3   8.5 x 14 inches, '
                                 '215.9 x 355.6 mm'),
                                ('Letter', 'Letter 2 8.5 x 11 inches, '
                                 '215.9 x 279.4 mm'),
                                ('Tabloid', 'Tabloid 29 279.4 x 431.8 mm'),
                                ('custom', 'Custom')],
                               string='Paper Type', default="custom",
                               help="Select Proper Paper size")
    col_no = fields.Integer('No. of Column')
    col_no_float = fields.Float('No of Column', readonly=True, help="Column Size without Rounding.")
    col_width = fields.Float('Column Width (mm)', default=52.5)
    col_height = fields.Float('Column Height (mm)', default=29.7)
    from_col = fields.Integer(string="Start Column", default=1)
    from_row = fields.Integer(string="Start Row", default=1)
    page_report_id = fields.Many2one('ir.ui.view', string='Page Report View', default=_get_page_report_id)
    column_report_design = fields.Text(string="Report Design", default=_get_page_report_design)
    make_update_existing = fields.Boolean(string="Update Existing Template")
    label_logo = fields.Binary(string="Label Logo")

    @api.model
    def dynamic_partner_address_wizard(self):
        partner_list_dict = []
        if self._context.get('active_ids') and self._context.get('active_model') == 'purchase.order':
            partner_list_dict += [(0, 0, {'partner_id': po.partner_id.id, 'qty': 1, 'line_id': po.id}) \
                                  for po in
                                  self.env['purchase.order'].search([('id', 'in', self._context.get('active_ids'))]) if
                                  po.partner_id]

        elif self._context.get('active_ids') and self._context.get('active_model') == 'sale.order':
            partner_list_dict += [(0, 0, {'partner_id': so.partner_id.id, 'qty': 1, 'line_id': so.id}) \
                                  for so in
                                  self.env['sale.order'].search([('id', 'in', self._context.get('active_ids'))]) if
                                  so.partner_id]

        elif self._context.get('active_ids') and self._context.get('active_model') == 'stock.picking':
            partner_list_dict += [(0, 0, {'partner_id': sp.partner_id.id, 'qty': 1, 'line_id': sp.id}) \
                                  for sp in
                                  self.env['stock.picking'].search([('id', 'in', self._context.get('active_ids'))]) if
                                  sp.partner_id]

        elif self._context.get('active_ids') and self._context.get('active_model') == 'account.move':
            partner_list_dict += [(0, 0, {'partner_id': invoice.partner_id.id, 'qty': 1, 'line_id': invoice.id}) \
                                  for invoice in
                                  self.env['account.move'].search([('id', 'in', self._context.get('active_ids'))]) if
                                  invoice.partner_id]

        elif self._context.get('active_ids') and self._context.get('active_model') == 'res.partner':
            partner_list_dict += [(0, 0, {'partner_id': partner.id, 'qty': 1}) \
                                  for partner in
                                  self.env['res.partner'].search([('id', 'in', self._context.get('active_ids'))]) if
                                  partner]

        if self._context.get('active_model'):
            design_id = self.env['partner.page.label.design'].search(
                [('report_model', '=', self._context.get('active_model'))], limit=1)
        else:
            design_id = self.env['partner.page.label.design'].search(
                [('report_model', '=', 'wizard.partner.page.report')], limit=1)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Reason',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.partner.page.report',
            'target': 'new',
            'context': {'default_design_id': design_id.id,
                        'default_partner_ids': partner_list_dict}
        }

    def action_print(self):
        if not self.partner_ids:
            raise UserError('Please, select partner(s) to print.')
        for partner in self.partner_ids:
            if partner.qty <= 0:
                 raise UserError('%s partner Address label qty should be greater then 0.!'
                            % (partner.partner_id.name))
        if (self.format == 'custom') and ((self.page_height <= 0) or (self.page_width <= 0)):
            raise UserError(_('You can not give page width and page height to zero(0).'))
        if (self.margin_top < 0) or (self.margin_left < 0) or \
            (self.margin_bottom < 0) or (self.margin_right < 0):
            raise UserError('Margin Value(s) for report can not be negative!')
        if (self.col_no <= 0):
            raise UserError(_('Minimun 1 column Required to print page labels in page.'))
        # for page
        if (self.col_height <= 0) or (self.col_width <= 0):
            raise UserError(_('Give proper hight and width for page column.'))
        if (self.from_col <= 0) or (self.from_row <= 0):
            raise UserError(_('Start row and column position should be 1 or greater.'))
        if self.from_col > self.col_no:
            raise UserError(_('Start column position can not be greater than no. of column.'))
        if self.with_barcode and (self.barcode_height <= 0 or self.barcode_width <= 0 or
                                  self.display_height <= 0 or self.display_width <= 0):
            raise UserError(_('Give proper barcode height and width values for display.'))
        data = self.read()[0]
        datas = {
            'ids': self._ids,
            'model': 'wizard.partner.page.report',
            'form': data
        }
        if self.page_report_id and self.column_report_design:
            self.page_report_id.sudo().write({'arch': self.column_report_design})
        if self.paper_format_id:
            if self.format == 'custom':
                result = self.paper_format_id.sudo().write({
                                        'format': self.format,
                                        'page_width': self.page_width,
                                        'page_height': self.page_height,
                                        'orientation': self.orientation,
                                        'margin_top': self.margin_top,
                                        'margin_left': self.margin_left,
                                        'margin_bottom': self.margin_bottom,
                                        'margin_right': self.margin_right,
                                        'dpi': self.dpi
                                    })
            else:
                result = self.paper_format_id.sudo().write({
                                        'format': self.format,
                                        'page_width': 0,
                                        'page_height': 0,
                                        'orientation': self.orientation,
                                        'margin_top': self.margin_top,
                                        'margin_left':self.margin_left,
                                        'margin_bottom': self.margin_bottom,
                                        'margin_right': self.margin_right,
                                        'dpi': self.dpi
                                    })
        return self.env.ref('dynamic_partner_address_label.dynamic_partner_page_report').report_action(self, data=datas)

    def save_design(self):
        if not self.make_update_existing:
            view_id = self.env.ref('dynamic_partner_address_label.wizard_partner_page_label_design_form_view').id
            ctx = dict(self.env.context)
            ctx.update({'wiz_id' : self.id})
            return {
                'name' : _('Partner Address Label Design'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'partner.page.label.design',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'view_id':view_id,
                'context' : ctx,
                'nodestroy': True
            }
        else:
            if self.design_id:
                self.design_id.write({
                                'page_template_design': self.column_report_design,
                                'report_model': self.report_model,
                                'page_width': self.page_width,
                                'page_height': self.page_height,
                                'dpi': self.dpi,
                                'margin_top': self.margin_top,
                                'margin_left': self.margin_left,
                                'margin_bottom': self.margin_bottom,
                                'margin_right': self.margin_right,
                                'orientation': self.orientation,
                                'humanReadable': self.humanReadable,
                                'barcode_height': self.barcode_height,
                                'barcode_width': self.barcode_width,
                                'display_height': self.display_height,
                                'display_width': self.display_width,
                                'with_barcode': self.with_barcode,
                                'format': self.format,
                                'col_no': self.col_no,
                                'col_width': self.col_width,
                                'col_height': self.col_height,
                                'label_logo': self.label_logo
                                })
                return {
                    'name': _('Partner Address Label'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'wizard.partner.page.report',
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
