# coding: utf-8
##################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)          #
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.                     #
# All Rights Reserved.                                                           #
#                                                                                #
# This program is copyright property of the author mentioned above.              #
# You can`t redistribute it and/or modify it.                                    #
#                                                                                #
##################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class TravelLocation(models.Model):
    _name = 'hr.emp.travel.location'
    _rec_name = 'dest_state_id'
    _description = "Travel Locations"

    travel_request_id_ref = fields.Many2one('hr.emp.travel.request')
    # travel_from
    source_street1 = fields.Char(string="From")
    source_street2 = fields.Char()
    source_state_id = fields.Many2one('res.country.state', string='State')
    source_country_id = fields.Many2one('res.country', string="Country")
    source_city = fields.Char()
    source_zip = fields.Integer()
    # travel_to
    dest_street1 = fields.Char(string="From")
    dest_street2 = fields.Char()
    dest_state_id = fields.Many2one('res.country.state', string='State')
    dest_country_id = fields.Many2one('res.country', string="Country")
    dest_city = fields.Char()
    dest_zip = fields.Integer()
    # travel Dates
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    # other details
    customer_id = fields.Many2one('res.partner', string="Customer")
    project_id = fields.Many2one('project.project', string="Customer")
    travel_days = fields.Integer(string="Days", compute="compute_days")
    reason = fields.Text(string="Reason")
    comment = fields.Text(string="Comment")

    # Days calculate
    @api.depends('start_date', 'end_date')
    def compute_days(self):
        for each in self:
            if each.start_date and each.end_date:
                d1 = datetime.strptime(str(each.end_date), '%Y-%m-%d')
                d2 = datetime.strptime(str(each.start_date), '%Y-%m-%d')
                daysDiff = (d1 - d2).days
                each.travel_days = int(daysDiff) + 1
            else:
                each.travel_days = 0

    # country selection on state
    @api.onchange('dest_state_id')
    def onchange_dest_state_id(self):
        for each in self:
            if each.dest_state_id:
                country = self.env['res.country.state'].search([('id', '=', each.dest_state_id.id)], limit=1)
                if country:
                    each.dest_country_id = country.country_id

    @api.onchange('source_state_id')
    def onchange_source_state_id(self):
        for each in self:
            if each.source_state_id:
                country = self.env['res.country.state'].search([('id', '=', each.source_state_id.id)], limit=1)
                if country:
                    each.source_country_id = country.country_id

    # Date Validation
    @api.onchange('start_date')
    def onchange_start_date(self):
        for each in self:
            if each.start_date:
                if (each.travel_request_id_ref.from_date > each.start_date) or (
                        each.travel_request_id_ref.to_date < each.start_date):
                    raise ValidationError(_((
                            "Please Enter Dates Between " + str(each.travel_request_id_ref.from_date) + " and " + str(
                        each.travel_request_id_ref.to_date))))
            if each.start_date and each.end_date:
                if each.end_date < each.start_date:
                    raise ValidationError(_("Please Enter Valid From Date \n it must be less than To Date"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        for each in self:
            if each.end_date:
                if (each.travel_request_id_ref.from_date > each.end_date) or (
                        each.travel_request_id_ref.to_date < each.end_date):
                    raise ValidationError(_(
                        "Please Enter Dates Between " + str(each.travel_request_id_ref.from_date) + " and " + str(each.travel_request_id_ref.to_date)))
            if each.start_date and each.end_date:
                if each.end_date < each.start_date:
                    raise ValidationError(_("Please Enter Valid From Date \n it must be less than To Date"))

    # constraints
    @api.constrains('start_date', 'end_date')
    def check_date(self):
        for each in self:
            if each.start_date and each.end_date:
                if each.end_date < each.start_date:
                    raise ValidationError(_("Please Enter Valid From Date \n it must be less than To Date"))
                elif each.start_date < each.travel_request_id_ref.from_date or each.start_date > each.travel_request_id_ref.to_date:
                    raise ValidationError(_("Please Check dates of Travel locations"))
                elif each.end_date < each.travel_request_id_ref.from_date or each.end_date > each.travel_request_id_ref.to_date:
                    raise ValidationError(_("Please Check dates of Travel locations"))
            else:
                raise ValidationError(_("Please Enter Dates"))


class TravelModes(models.Model):
    _name = 'hr.emp.travel.mode'
    _description = "Mode of Travelling"

    name = fields.Text(string="Mode")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: