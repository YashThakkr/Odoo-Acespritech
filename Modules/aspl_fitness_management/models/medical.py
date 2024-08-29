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

from odoo import models, fields


class MedicalSurgery(models.Model):
    _name = 'medical.surgery'
    _description = 'Medical Surgery'

    name = fields.Char("Name")
    description = fields.Text('description')


class SubscriberMedicalSurgery(models.Model):
    _name = 'subscriber.medical.surgery'
    _description = 'Subscriber Medical Surgery'
    _rec_name = 'surgery_id'

    surgery_id = fields.Many2one('medical.surgery', string="Surgery")
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    date = fields.Date("Date")
    desc = fields.Text("Description")
    surgen_name = fields.Char("Surgen Name")
    instruction = fields.Char("Instruction")
    state = fields.Selection(
        [('undergo', 'Undergo'), ('treatment', 'Treatment'), ('recovered', 'Recevored')],
        string="State", default="undergo")


class MedicalDiagnose(models.Model):
    _name = 'medical.diagnose'
    _description = 'Medical Diagnose'

    name = fields.Char("Name")
    description = fields.Text('description')


class SubscriberMedicalDiagnose(models.Model):
    _name = 'subscriber.medical.diagnose'
    _description = 'Subscriber Medical Diagnose'
    _rec_name = 'diagnose_id'

    diagnose_id = fields.Many2one("medical.diagnose")
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    desc = fields.Text("Description")
    state = fields.Selection([('ongoing', 'Ongoing'), ('recovered', 'Recevored')], string="State",
                             default="ongoing")


class MedicalSymptom(models.Model):
    _name = 'medical.symptom'
    _description = 'Medical Symptom'

    name = fields.Char("Name")
    description = fields.Text('description')


class SubscriberMedicalSymptom(models.Model):
    _name = 'subscriber.medical.symptom'
    _description = 'Subscriber Medical Symptom'
    _rec_name = 'symptom_id'

    symptom_id = fields.Many2one('medical.symptom', string="Symptom")
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    desc = fields.Text("Description")
    state = fields.Selection([('ongoing', 'Ongoing'), ('recovered', 'Recevored')], string="State",
                             default="ongoing")


class AllergyType(models.Model):
    _name = "allergy.type"
    _description = "Allergy Type"

    name = fields.Char("Name")
    description = fields.Text('description')


class SubscriberAllergy(models.Model):
    _name = "subscriber.allergy"
    _description = "Subscriber Allergy"
    _rec_name = 'allergy_type_id'

    allergy_type_id = fields.Many2one('allergy.type', string="Type")
    subscriber_id = fields.Many2one('res.partner', string="Subscriber")
    desc = fields.Text("Description")
    state = fields.Selection([('existing', 'Existing'), ('recovered', 'Recovered')], string="State",
                             default="existing")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
