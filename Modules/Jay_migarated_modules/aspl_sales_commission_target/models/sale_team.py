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

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.constrains('sale_team_comm_ids', 'sale_team_dist_comm_ids', 'sale_team_cons_comm_ids')
    def _check_commission_values(self):
        if self.sale_team_comm_ids.filtered(
                lambda line: line.compute_price_type == 'per' and
                             line.commission > 100 or line.commission < 0.0):
            raise UserError(_('Commission value for Percentage type must be between 0 to 100.'))
        if self.sale_team_dist_comm_ids.filtered(
                lambda line: line.compute_price_type == 'per' and
                             line.commission > 100 or line.commission < 0.0):
            raise UserError(_('Commission value for Percentage type must be between 0 to 100.'))
        if self.sale_team_cons_comm_ids.filtered(
                lambda line: line.compute_price_type == 'per' and
                             line.commission > 100 or line.commission < 0.0):
            raise UserError(_('Commission value for Percentage type must be between 0 to 100.'))

    sale_team_comm_ids = fields.One2many('sales.team.commission', 'sale_team_id',
                                         string="Sales Person Commission")
    sale_team_dist_comm_ids = fields.One2many('sales.team.distributor.commission', 'sale_team_id',
                                              string="Distributor Commission")
    sale_team_cons_comm_ids = fields.One2many('sales.team.consultant.commission', 'sale_team_id',
                                              string="Consultant Commission")


class SalesTeamCommission(models.Model):
    _description = 'Sale Team Commission'
    _name = 'sales.team.commission'

    @api.onchange('job_id')
    def onchange_job_id(self):
        self.user_ids = False

    @api.onchange('commission', 'compute_price_type')
    def onchange_commission(self):
        if self.commission and self.compute_price_type == 'per' and \
                (self.commission < 0.0 or self.commission > 100):
            raise UserError(
                _('Entered Commission is %s. \n Commission value for '
                  'Percentage type must be between 0 to 100. ') % self.commission)

    job_id = fields.Many2one('hr.job', string="Job Position")
    user_ids = fields.Many2many('res.users', string="User(s)")
    compute_price_type = fields.Selection([('fix_price', 'Fix Price'), ('per', 'Percentage')],
                                          string="Compute Price", default="per", required=True)
    commission = fields.Float(string="Commission")
    sale_team_id = fields.Many2one('crm.team', string="Sale Team")


class SalesTeamDistributorCommission(models.Model):
    _description = 'Sale Team Distributor Commission'
    _name = 'sales.team.distributor.commission'

    @api.onchange('commission', 'compute_price_type')
    def onchange_commission(self):
        if self.commission and self.compute_price_type == 'per' and \
                (self.commission < 0.0 or self.commission > 100):
            raise UserError(
                _('Entered Commission is %s. \n Commission value for '
                  'Percentage type must be between 0 to 100. ') % self.commission)

    partner_id = fields.Many2one('res.partner', string="Distributor")
    compute_price_type = fields.Selection([('fix_price', 'Fix Price'),
                                           ('per', 'Percentage')],
                                          string="Compute Price", default="per", required=True)
    commission = fields.Float(string="Commission")
    sale_team_id = fields.Many2one('crm.team', string="Sale Team")


class SalesTeamConsultantCommission(models.Model):
    _description = 'Sale Team Consultant Commission'
    _name = 'sales.team.consultant.commission'

    @api.onchange('commission', 'compute_price_type')
    def onchange_commission(self):
        if self.commission and self.compute_price_type == 'per' and \
                (self.commission < 0.0 or self.commission > 100):
            raise UserError(
                _('Entered Commission is %s. \n Commission value for '
                  'Percentage type must be between 0 to 100. ') % self.commission)

    partner_id = fields.Many2one('res.partner', string="Consultant")
    compute_price_type = fields.Selection([('fix_price', 'Fix Price'),
                                           ('per', 'Percentage')],
                                          string="Compute Price", default="per", required=True)
    commission = fields.Float(string="Commission")
    sale_team_id = fields.Many2one('crm.team', string="Sale Team")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
