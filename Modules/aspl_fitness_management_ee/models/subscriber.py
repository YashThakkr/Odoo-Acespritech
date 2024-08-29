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

import logging
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


class SubscriberPlan(models.Model):
    _name = 'subscriber.plan'
    _description = 'Subscriber Plan'

    branch_time_range_id = fields.Many2one('batch.duration.line', string="Batch Duration",
                                           ondelete='restrict')
    schedule_ids = fields.One2many('subscriber.schedule', 'plan_id', string="Schedule")
    start_time = fields.Float("Start Time")
    end_time = fields.Float("End Time")
    joining_date = fields.Date("Joining Date", default=fields.Date.today)
    ending_date = fields.Date("Ending Date")
    active = fields.Boolean("Active", default=True)
    name = fields.Char("Name", default="New", copy=False)

    def _default_pricelist(self):
        return self.env['product.pricelist'].search([
            ('company_id', 'in', (False, self.env.company.id)),
            ('currency_id', '=', self.env.company.currency_id.id)], limit=1)

    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist",
                                   default=_default_pricelist)

    @api.depends('service_line_ids', 'service_line_ids.fees', 'nutrition_fees')
    def _compute_plan_fees(self):
        for plan in self:
            plan_fees = sum([each.fees for each in plan.service_line_ids]) or 0.0
            plan.plan_fees = plan_fees or 0.0
            plan.fees_total = plan_fees + (plan.nutrition_fees or 0.0)

    plan_fees = fields.Float("Plan Fees", compute="_compute_plan_fees", store=True)
    gym_plan_id = fields.Many2one('gym.plan', string="Plan")

    @api.depends('invoice_ids.payment_state')
    def _compute_state(self):
        for each in self:
            if each.invoice_ids and all([inv.payment_state == 'paid' for inv in each.invoice_ids]):
                each.state = "paid"

    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('validated', 'Validated'),
                              ('paid', 'Paid'),
                              ('cancel', 'Cancel')], string="State", default="draft", store=True,
                             compute="_compute_state", copy=False)
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    service_line_ids = fields.One2many('gym.service.line', 'subscriber_plan_id', string="Service",
                                       copy=True)
    nutrition_fees = fields.Float("Nutrition Fees", store=True)
    fees_total = fields.Float("Total Fees", compute="_compute_plan_fees", store=True)
    nutrition_line_ids = fields.One2many('nutrition.plan.lines', 'plan_id', string='Nutrition')
    meal_ids = fields.Many2many('nutrition.meal', 'nutrition_subscriber_plan_rel', 'plan_id',
                                'meal_id', string="Meals")
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Term")
    branch_id = fields.Many2one('company.branch', string="Branch")
    plan_type = fields.Selection([('nutrition', 'Nutrition'), ('gym', 'Gym'),
                                  ('both', 'Gym & Nutrition')],
                                 string="Type", copy=False)
    invoice_ids = fields.One2many('account.move', 'plan_id', string="Invoices", copy=False,
                                  ondelete='restrict')
    nutrition_invoice = fields.Boolean(string="Nutrition Invoice", copy=False)

    def branch_ids(self):
        bids_lst = []
        if request.httprequest.cookies.get('bids'):
            for branch in request.httprequest.cookies.get('bids'):
                if branch.isnumeric():
                    branch_id = request.env['company.branch'].sudo().browse(
                        int(branch))
                    if branch_id.exists():
                        bids_lst.append(int(branch))
        return bids_lst

    @api.onchange('branch_id')
    def onchange_branch_id(self):
        """
        :return:
        """
        branch_time_range_ids = []
        if self.branch_id:
            duration = self.env['batch.duration'].search([('branch_id', '=', self.branch_id.id)])
            if duration:
                branch_time_range_ids = duration.line_ids.ids
        return {'domain': {'branch_time_range_id': [('id', 'in', branch_time_range_ids)]}}

    @api.constrains('subscriber_id', 'ending_date')
    def _check_plan_membership_date(self):
        if self.plan_type in ['gym', 'both']:
            if self.subscriber_id.membership_history_ids:
                membership_ending_date = self.env['subscriber.membership.history'].browse(
                    max(self.subscriber_id.membership_history_ids.ids)).end_date
                if membership_ending_date and membership_ending_date <= self.ending_date:
                    raise UserError(
                        "Your membership expires before your plan so please extend "
                        "your membership!")
            else:
                raise UserError("You should have at least one active membership"
                                " to subscribe gym plan!")

    @api.onchange('branch_time_range_id')
    def _onchange_time_range(self):
        if self.branch_time_range_id:
            self.branch_id = self.branch_time_range_id.batch_id.branch_id.id
            self.start_time = self.branch_time_range_id.start_time
            self.end_time = self.branch_time_range_id.end_time

    @api.onchange('subscriber_id')
    def _onchange_subscriber_id(self):
        if self.subscriber_id:
            self.payment_term_id = self.subscriber_id.property_payment_term_id.id \
                if self.subscriber_id.property_payment_term_id else False
            self.branch_id = self.subscriber_id.branch_id and \
                             self.subscriber_id.branch_id.id or False

    @api.constrains('start_time', 'end_time')
    def _check_validity_start_end_time(self):
        for each in self:
            if each.start_time and each.end_time and each.end_time < each.start_time:
                raise ValidationError(_('End time must be greater than start time.'))

    @api.onchange('gym_plan_id', 'joining_date')
    def _onchange_gym_plan_joining_date(self):
        if self.joining_date and self.gym_plan_id and self.gym_plan_id.start_date and self.gym_plan_id.end_date:
            days = (self.gym_plan_id.end_date - self.gym_plan_id.start_date).days
            self.ending_date = self.joining_date + timedelta(days=days)
        service_lst = []
        if self.gym_plan_id:
            for each in self.gym_plan_id.plan_line_ids:
                service_id = self.env['gym.service.line'].create({'service_id': each.service_id.id,
                                                                  'description': each.desc,
                                                                  'fees': each.fees,
                                                                  'subscriber_plan_id': self.id})
                service_lst.append(service_id.id)
            self.service_line_ids = [(6, 0, service_lst)]

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env["ir.sequence"].next_by_code("subscriber.fitness.plan")
        if vals.get('branch_time_range_id'):
            time_range_id = self.env['batch.duration.line'].browse(vals.get('branch_time_range_id'))
            if time_range_id and time_range_id.batch_id and time_range_id.batch_id.branch_id:
                vals['branch_id'] = time_range_id.batch_id.branch_id.id
        res = super(SubscriberPlan, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('branch_time_range_id'):
            time_range_id = self.env['batch.duration.line'].browse(vals.get('branch_time_range_id'))
            if time_range_id and time_range_id.batch_id and time_range_id.batch_id.branch_id:
                vals['branch_id'] = time_range_id.batch_id.branch_id.id
        return super(SubscriberPlan, self).write(vals)

    def enable_nutrition_plan(self):
        self.write({'plan_type': 'both', 'nutrition_invoice': True})
        self.subscriber_id.nutrition_subscriber = True

    def create_plan_invoice(self):
        lst = []

        if self.plan_type in ['gym', 'both']:
            for each in self.service_line_ids:
                lst.append((0, 0, {'name': each.service_id.name,
                                   'price_unit': each.fees,
                                   'product_id': each.service_id.id,
                                   'quantity': 1.0,
                                   'tax_ids': [(6, 0, each.service_id.taxes_id.ids)]
                                   if each.service_id.taxes_id else False,
                                   'branch_id': self.branch_id.id
                                   }))
            if self.nutrition_invoice and self.plan_type == 'both':
                category = self.env.ref('product.product_category_all')
                lst.append((0, 0, {'name': self.name,
                                   'price_unit': self.nutrition_fees,
                                   'account_id': category.property_account_income_categ_id.id,
                                   'quantity': 1.0,
                                   'branch_id': self.branch_id.id
                                   }))
            self.env['account.move'].create({'partner_id': self.subscriber_id.id,
                                             'move_type': 'out_invoice',
                                             'invoice_payment_term_id': self.payment_term_id.id
                                             if self.payment_term_id else False,
                                             'branch_id': self.branch_time_range_id.batch_id.branch_id.id,
                                             'invoice_date': date.today(),
                                             'invoice_line_ids': lst,
                                             'plan_id': self.id
                                             })
            self.state = 'confirm'
            self.nutrition_invoice = False
        if self.plan_type == 'nutrition':
            category = self.env.ref('product.product_category_all')
            invoice_line = [(0, 0, {'name': self.name,
                                    'price_unit': self.nutrition_fees,
                                    'account_id': category.property_account_income_categ_id.id,
                                    'quantity': 1.0,
                                    'branch_id': self.branch_id.id
                                    })]
            self.env['account.move'].create({'partner_id': self.subscriber_id.id,
                                             'move_type': 'out_invoice',
                                             'invoice_payment_term_id': self.payment_term_id.id
                                             if self.payment_term_id else False,
                                             'branch_id': self.branch_id.id,
                                             'invoice_date': date.today(),
                                             'invoice_line_ids': invoice_line,
                                             'plan_id': self.id
                                             })
            self.state = 'confirm'

    def add_nutrition_invoice(self):
        existing_invoice_id = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')

        if self.plan_type == 'both':
            category = self.env.ref('product.product_category_all')
            invoice_line = [(0, 0, {'name': self.name,
                                    'price_unit': self.nutrition_fees,
                                    'account_id': category.property_account_income_categ_id.id,
                                    'quantity': 1.0,
                                    'branch_id': self.branch_id.id
                                    })]
            if existing_invoice_id:
                existing_invoice_id[0].invoice_line_ids = invoice_line
            else:
                self.env['account.move'].create({'partner_id': self.subscriber_id.id,
                                                 'move_type': 'out_invoice',
                                                 'invoice_payment_term_id': self.payment_term_id.id
                                                 if self.payment_term_id else False,
                                                 'branch_id': self.branch_id.id,
                                                 'invoice_date': date.today(),
                                                 'invoice_line_ids': invoice_line,
                                                 'plan_id': self.id
                                                 })
            self.nutrition_invoice = False

    def action_register_gym_payment(self):
        branch_id = self.branch_time_range_id.batch_id.branch_id.id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.register',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Register Payment',
            'view_id': self.env.ref('account.view_account_payment_register_form').id,
            'context': {'default_invoice_ids': [(4, self.invoice_ids.ids, None)],
                        'active_model': 'account.move',
                        'active_ids': self.invoice_ids.ids,
                        'plan_branch_id': branch_id,
                        'gym_plan_id': self.id,
                        'only_full_payment': True}
        }
        return action

    def create_nutrition_schedule(self):
        lst = []
        date_range = [self.joining_date + timedelta(days=x) for x in range(
            (self.ending_date - self.joining_date).days + 1)]

        for each in range(1, 8):
            line_id = self.env['nutrition.plan.lines'].create({'plan_id': self.id,
                                                               'day': str(each),
                                                               'meal_ids': [(6, 0,
                                                                             [meal.id for meal in
                                                                              self.meal_ids])]})
            lst.append(line_id.id)
        self.nutrition_line_ids = [(6, 0, lst)]

    def action_update_schedule(self):

        if self.plan_type in ['nutrition', 'both']:
            self.create_nutrition_schedule()

        if self.plan_type in ['gym', 'both']:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'create.subscriber.schedule',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'name': 'Gym Schedules',
                'context': "{'default_subscriber_id': %s, 'default_type': 'gym',"
                           " 'default_plan_id' : %s, "
                           "'default_gym_service_ids': %s}"
                           % (self.subscriber_id.id,
                              self.gym_plan_id.id,
                              [(6, 0,
                                [line.service_id.id for line in self.service_line_ids
                                 if line.service_id])]),
            }

    def view_subscriber_plan_invoices(self):
        action = self.env.ref('aspl_fitness_management_ee.act_subscriber_plan_2_invoice').read()[0]
        if len(self.invoice_ids.ids) > 1:
            action['domain'] = [('id', 'in', self.invoice_ids.ids)]
        elif len(self.invoice_ids.ids) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.invoice_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_sent_invoice(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env['res.config.settings'].get_values()['invoice_mail_tmp_id']
        except ValueError:
            template_id = False
        template_rec = self.env['mail.template'].browse(template_id) if template_id else False
        if template_rec and template_rec.lang:
            try:
                compose_form_id = ir_model_data._xmlid_to_res_id(
                    'mail.email_compose_message_wizard_form')
            except ValueError:
                compose_form_id = False
            lang = self.env.context.get('lang')
            if template_rec.lang:
                lang = template_rec._render_lang(self.invoice_ids.ids).get(
                    self.invoice_ids.ids[0])
            else:
                lang = lang.code
            ctx = {
                'default_model': 'account.move',
                'active_model': 'account.move',
                'active_id': self.invoice_ids.ids[0],
                'active_ids': self.invoice_ids.ids,
                'default_res_id': self.invoice_ids.ids[0],
                'plan_id': self.id,
                'default_use_template': bool(template_rec.id),
                'default_template_id': template_rec.id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "mail.mail_notification_paynow",
                'proforma': self.env.context.get('proforma', False),
                'model_description': self.invoice_ids[0].with_context(lang=lang).type_name,
                'force_email': True
            }
            dict = {
                'name': 'Send Invoice',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }
            return dict
        else:
            raise ValidationError(
                _("Invoice mail template is not available for subscriber plan ! "))

    def validate_invoice_and_plan(self):
        if hasattr(self.env['account.move'], 'l10n_in_gst_treatment'):
            for move in self.invoice_ids:
                if not move.l10n_in_gst_treatment:
                    if move.partner_id.l10n_in_gst_treatment:
                        move.l10n_in_gst_treatment = move.partner_id.l10n_in_gst_treatment
                    else:
                        move.l10n_in_gst_treatment = 'unregistered'
        if all([each.amount_residual == 0.0 for each in self.invoice_ids]):
            self.write({'state': 'paid'})
            return True
        self.invoice_ids.action_post()
        self.write({'state': 'validated'})

    @api.model
    def month_wise_collection(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                subscriber_plan_query = "select * from subscriber_plan where " \
                                           "active = true and state = 'paid' and branch_id = {} " \
                                           "or branch_id is null and plan_type in ('gym', 'nutrition', 'both');".format(bids_tpl)
                self._cr.execute(subscriber_plan_query)
            else:
                bids_tpl = tuple(bids_lst)
                subscriber_plan_query = "select * from subscriber_plan where " \
                                           "active = true and state = 'paid' and branch_id in {} " \
                                           "or branch_id is null and plan_type in ('gym', 'nutrition', 'both');".format(bids_tpl)
                self._cr.execute(subscriber_plan_query)
            subscriber_ids = self._cr.dictfetchall()
            monthly_collection = []
            current_time = datetime.now()
            for month in range(1,13):
                amount = 0
                for subscriber_id in subscriber_ids:
                    if subscriber_id.get('joining_date').strftime('%m') == str(month) and subscriber_id.get('joining_date').strftime('%Y') == current_time.strftime('%Y'):
                        amount += int(subscriber_id.get('plan_fees'))
                monthly_collection.append(amount)
            return monthly_collection

    @api.model
    def year_wise_collection(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                subscriber_plan_query = "select * from subscriber_plan where " \
                                           "active = true and state != 'draft' and branch_id = {} " \
                                           "or branch_id is null and plan_type in ('gym', 'nutrition', 'both');".format(bids_tpl)
                self._cr.execute(subscriber_plan_query)
            else:
                bids_tpl = tuple(bids_lst)
                subscriber_plan_query = "select * from subscriber_plan where " \
                                           "active = true and state != 'draft' and branch_id in {} " \
                                           "or branch_id is null and plan_type in ('gym', 'nutrition', 'both');".format(bids_tpl)
                self._cr.execute(subscriber_plan_query)
            subscriber_plan_ids = self._cr.dictfetchall()
            last_years = []
            yearly_collection = []
            current_year = date.today().year
            for count in range(0,5):
                last_years.insert(0, current_year - count)
            for year in last_years:
                amount = 0
                for subscriber_id in subscriber_plan_ids:
                    if subscriber_id.get('joining_date').strftime('%Y') == str(year):
                        amount += int(subscriber_id.get('plan_fees'))
                yearly_collection.append(amount)
            return yearly_collection

    @api.model
    def past_month_collection(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                subscriber_plan_query = "select * from subscriber_plan where " \
                                           "active = true and state = 'paid' and branch_id = {} " \
                                           "or branch_id is null and plan_type in ('gym', 'nutrition', 'both');".format(bids_tpl)
                self._cr.execute(subscriber_plan_query)
            else:
                bids_tpl = tuple(bids_lst)
                subscriber_plan_query = "select * from subscriber_plan where " \
                                           "active = true and state = 'paid' and branch_id in {} " \
                                           "or branch_id is null and plan_type in ('gym', 'nutrition', 'both');".format(bids_tpl)
                self._cr.execute(subscriber_plan_query)
            subscriber_plan_ids = self._cr.dictfetchall()
            current_time = datetime.now()
            start_date = current_time - timedelta(30)
            amount = 0
            for subscriber_id in subscriber_plan_ids:
                if subscriber_id.get('joining_date') >= start_date.date():
                    amount += int(subscriber_id.get('plan_fees'))
            return amount

    @api.model
    def user_by_branch(self):
        bids_lst = self.branch_ids()
        if bids_lst:
            if len(bids_lst) == 1:
                bids_tpl = bids_lst[0]
                subscriber_plan_query = "select * from subscriber_plan where " \
                                           "active = true and state != 'draft' or state != 'cancel' and branch_id = {} " \
                                           "or branch_id is null and plan_type in ('gym', 'nutrition', 'both');".format(bids_tpl)
                self._cr.execute(subscriber_plan_query)
            else:
                bids_tpl = tuple(bids_lst)
                subscriber_plan_query = "select * from subscriber_plan where " \
                                           "active = true and state != 'draft' or state != 'cancel' and branch_id in {} " \
                                           "or branch_id is null and plan_type in ('gym', 'nutrition', 'both');".format(bids_tpl)
                self._cr.execute(subscriber_plan_query)
                bids_lst = sorted(bids_lst)
            subscriber_plan_ids = self._cr.dictfetchall()
            users_by_branch = []
            for branch_id in bids_lst:
                amount = 0
                for subscriber_plan_id in subscriber_plan_ids:
                    if branch_id == subscriber_plan_id.get('branch_id'):
                        amount += 1
                users_by_branch.append(amount)
            return users_by_branch


class MedicationType(models.Model):
    _name = 'medication.type'
    _description = 'Medication Type'

    name = fields.Char("Name")
    description = fields.Text('description')


class SubscriberMedication(models.Model):
    _name = 'subscriber.medication'
    _description = 'Subscriber Medication'
    _rec_name = 'type_id'

    type_id = fields.Many2one('medication.type', string="Type")
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    reason = fields.Char("Reason")
    dosage = fields.Char("Dosage")
    desc = fields.Char("Description")
    state = fields.Selection([('ongoing', 'Ongoing'), ('completed', 'Completed')], string="State",
                             default="ongoing")


class SubscriberSchedule(models.Model):
    _name = 'subscriber.schedule'
    _description = 'Subscriber Schedule'

    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], index=True, default='0', string="Day")

    plan_id = fields.Many2one('subscriber.plan', string="Plan")
    line_ids = fields.Many2many('schedule.line', string="Lines")


class ScheduleLine(models.Model):
    _name = 'schedule.line'
    _description = 'Schedule Lines'
    _rec_name = 'exercise_id'

    exercise_id = fields.Many2one('gym.exercise', string="Exercise")
    count = fields.Float("Count")
    uom_id = fields.Many2one('uom.uom', string="Unit")


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        user_rec = self.env['res.users'].sudo().browse(self._uid).branch_ids.ids
        if user_rec:
            sql = """SELECT id FROM res_partner
                        WHERE branch_id in %s""" % (" (%s) " % ','.join(map(str, user_rec)))
            self._cr.execute(sql)
            result = self._cr.fetchall()
            rec = [each[0] for each in result]
            domain += ['|', ('id', 'in', rec), ('branch_id', '=', False)]
            return super(ResPartner, self).search(domain, offset=offset, limit=limit,
                                                  order=order, count=count)
        return super(ResPartner, self).search(domain, offset=offset, limit=limit,
                                              order=order, count=count)

    @api.depends('birth_date')
    def _compute_age(self):
        for each in self:
            if each.birth_date:
                each.age = (date.today() - each.birth_date) // timedelta(days=365)
            else:
                each.age = 0

    @api.depends('membership_history_ids')
    def count_membership(self):
        """
        Count Member membership
        :return: Integer number
        """
        for rec in self:
            rec.membership_history_count = len(rec.membership_history_ids.ids)

    branch_id = fields.Many2one(
        'company.branch', string="Branch", default=lambda self: self.env.user.branch_id)
    birth_date = fields.Date("Birth Date")
    age = fields.Integer("Age", compute="_compute_age", store=1)
    gender = fields.Selection([
        ('Female', 'Female'), ('Male', 'Male'), ('Others', 'Others')], string="Gender",
        default="Male")
    gym_subscriber = fields.Boolean("Gym Subscriber")
    nutrition_subscriber = fields.Boolean("Nutrition Subscriber")
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist ")
    allergy = fields.Boolean("Allergy")
    allergy_ids = fields.One2many('subscriber.allergy', 'subscriber_id', string="Allergies")
    symptoms = fields.Boolean("Symptoms")
    symptoms_ids = fields.One2many('subscriber.medical.symptom', 'subscriber_id',
                                   string="Symptom")
    diagnoses = fields.Boolean("Diagnose")
    diagnose_ids = fields.One2many('subscriber.medical.diagnose', 'subscriber_id',
                                   string="Diagnosis")
    surgery = fields.Boolean("Surgery")
    surgery_ids = fields.One2many('subscriber.medical.surgery', 'subscriber_id', string="Surgeries")
    physical_activities = fields.Boolean("Physical Activities")
    physical_activity_ids = fields.One2many('subscriber.physical.activity', 'subscriber_id',
                                            string="Activity")
    medications = fields.Boolean("Medication")
    medication_ids = fields.One2many('subscriber.medication', 'subscriber_id', string="Medications")
    risk_factors = fields.Boolean("Risk Factors")
    risk_factor_ids = fields.One2many('subscriber.risk.factor', 'subscriber_id', string="Risk")
    fitness_goal_ids = fields.One2many('subscriber.fitness.goal', 'subscriber_id',
                                       string="Fitness Goal")
    gym_plan_count = fields.Integer(string="Gym Plans")
    weight_history_ids = fields.One2many(
        'weight.history', 'partner_id', 'Weight History')

    def _compute_plan_count(self):
        for each in self:
            each.plan_count = self.env['subscriber.plan'].search_count(
                [('subscriber_id', '=', each.id)])

    plan_count = fields.Integer(string="Subscriber Plans", compute="_compute_plan_count")
    membership_history_ids = fields.One2many('subscriber.membership.history', 'subscriber_id',
                                             string="Membership History")
    membership_history_count = fields.Integer('Membership Count', compute=count_membership)

    def open_members_membership(self):
        """
        :return:
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'subscriber.membership.history',
            'view_mode': 'tree,form',
            'name': 'Membership History',
            'domain': [('id', 'in', self.membership_history_ids.ids)],
        }

    def get_action_subscriber_plan_tree(self):
        subscriber_plans = self.env['subscriber.plan'].search([('subscriber_id', '=', self.id)])
        action = \
            self.env.ref('aspl_fitness_management_ee.action_subscriber_to_subscriber_plan').read()[0]
        if len(subscriber_plans) > 1:
            action['domain'] = [('id', 'in', subscriber_plans.ids)]
        elif len(subscriber_plans.ids) == 1:
            action['views'] = [
                [self.env.ref('aspl_fitness_management_ee.view_subscriber_plan_form').id, 'form'],
                [self.env.ref('aspl_fitness_management_ee.view_subscriber_plan_tree').id, 'tree']]
            action['res_id'] = subscriber_plans.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def default_get(self, field_list):
        result = super(ResPartner, self).default_get(field_list)
        if self._context.get('fitness_subscribers') and 'company_id' in field_list:
            result['company_id'] = self.env.company.id
            result['branch_id'] = self.env.user.current_branch_id.id
        return result

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if res.email:
            template = self.env['res.config.settings'].get_values()
            try:
                template_id = self.env['mail.template'].browse([template['welcome_mail_tmp_id']])
                if template_id:
                    template_id.send_mail(res.id, force_send=False, raise_exception=False)
                    _logger.info('Mail Sended to %s' % (self.name))
            except Exception:
                _logger.warning('Mail Server not Configured', exc_info=True)
        return res


    @api.model
    def get_fitness_data(self):
        bids_lst = []
        if request.httprequest.cookies.get('bids'):
            for branch in request.httprequest.cookies.get('bids'):
                if branch.isnumeric():
                    branch_id = request.env['company.branch'].sudo().browse(
                        int(branch))
                    if branch_id.exists():
                        bids_lst.append(int(branch))
        if len(bids_lst) == 1:
            bids_tpl = bids_lst[0]
            members_count_query = """select * from res_partner where"""
            if bids_tpl:
                members_count_query += ' branch_id = {} or branch_id is null AND ' \
                                       'gym_subscriber = true or branch_id = {} ' \
                                       'or branch_id is null AND ' \
                                       'nutrition_subscriber = true;'.format(
                    bids_tpl, bids_tpl)
            else:
                members_count_query += ' gym_subscriber = true or nutrition_subscriber = true;'
        else:
            bids_tpl = tuple(bids_lst)
            members_count_query = """select * from res_partner where"""
            if bids_tpl:
                members_count_query = """select * from res_partner where"""
                members_count_query += ' branch_id in {} or branch_id is null AND ' \
                                       'gym_subscriber = true or branch_id in {} ' \
                                       'or branch_id is null AND ' \
                                       'nutrition_subscriber = true;'.format(
                    bids_tpl, bids_tpl)
            else:
                members_count_query += ' gym_subscriber = true or nutrition_subscriber = true;'
        self._cr.execute(members_count_query)
        members_ids = self._cr.dictfetchall()
        if bids_tpl:
            if type(bids_tpl) != tuple:
                membership_history_ids = self.env["subscriber.membership.history"].search\
                    ([('state', 'not in', ('draft','cancelled')),('branch_id', 'in', (False, bids_tpl))])
            else:
                temp_bids_tpl = list(bids_tpl)
                temp_bids_tpl.append(False)
                temp_bids_tpl = tuple(temp_bids_tpl)
                membership_history_ids = self.env["subscriber.membership.history"].search\
                    ([('state', 'not in', ('draft','cancelled')),('branch_id', 'in', temp_bids_tpl)])
        subscriber_plan_query = ''
        if bids_tpl:
            if type(bids_tpl) != tuple:
                subscriber_plan_query = \
                    "select * from subscriber_plan where branch_id = {} or " \
                    "branch_id is null and active = true and plan_type in ('gym', 'nutrition', " \
                    "'both');".format(bids_tpl, bids_tpl)
            else:
                subscriber_plan_query = \
                    "select * from subscriber_plan where branch_id in {} or " \
                    "branch_id is null and active = true and plan_type in ('gym', 'nutrition', " \
                    "'both');".format(bids_tpl, bids_tpl)
        self._cr.execute(subscriber_plan_query)
        subscriber_plan_ids = self._cr.dictfetchall()
        product_query = "select * from product_template where is_gym_service = true;"
        if bids_tpl:
            if type(bids_tpl) != tuple:
                product_query = \
                    "select * from product_template where is_gym_service = true " \
                    "AND branch_id = {}".format(bids_tpl)
            else:
                product_query = \
                    "select * from product_template where is_gym_service = true " \
                    "AND branch_id in {}".format(bids_tpl)
        self._cr.execute(product_query)
        product_ids = self._cr.dictfetchall()
        data = {
            'total_members': len(members_ids),
            'membership_history': len(membership_history_ids),
            'subscriber_plan': len(subscriber_plan_ids),
            'product_ids': len(product_ids),
        }
        return data


class WeightHistory(models.Model):
    _name = 'weight.history'
    _description = 'Weight History'

    weight = fields.Float('Weight(Kg)')
    date = fields.Date('Date', default=date.today())
    partner_id = fields.Many2one('res.partner', 'Partner')


class FitnessGoal(models.Model):
    _name = 'fitness.goal'
    _description = 'Fitness Goal'

    name = fields.Char("Name")
    desc = fields.Text("Description")


class SubscriberFitnessGoal(models.Model):
    _name = 'subscriber.fitness.goal'
    _description = 'Subscriber Fitness Goal'
    _rec_name = 'fitness_goal_id'

    fitness_goal_id = fields.Many2one('fitness.goal', string="Goal")
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    desc = fields.Text("Description")
    duration = fields.Integer("Duration")
    duration_type = fields.Selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'),
                                      ('years', 'Years')],
                                     string="Duration Type", default="days")
    state = fields.Selection(
        [('new', 'New'), ('progress', 'In Progress'), ('archived', 'Archived')],
        string="State", default="new")


class PhysicalActivity(models.Model):
    _name = 'physical.activity'
    _description = 'Physical Activity'

    name = fields.Char("Name")
    description = fields.Text('description')


class SubscriberPhysicalActivity(models.Model):
    _name = 'subscriber.physical.activity'
    _description = 'Subscriber Physical Activity'
    _rec_name = 'activity_id'

    activity_id = fields.Many2one('physical.activity', string="Activity")
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    desc = fields.Text("Description")


class RiskFactorType(models.Model):
    _name = 'risk.factor.type'
    _description = 'Risk Factor Type'

    name = fields.Char("Name")
    description = fields.Text('description')


class SubscriberRiskFactor(models.Model):
    _name = 'subscriber.risk.factor'
    _description = 'Subscriber Risk Factor'
    _rec_name = 'type_id'

    type_id = fields.Many2one('risk.factor.type', string="Type")
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    desc = fields.Text("Description")
    risk_level = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                                  string="Risk Level",
                                  default="low")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
