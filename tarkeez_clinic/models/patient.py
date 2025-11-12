# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TarkeezPatient(models.Model):
    _name = 'tarkeez.patient'
    _description = 'Tarkeez Patient'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    arabic_name = fields.Char(string='Arabic Name')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')

    appointment_ids = fields.One2many(
        'tarkeez.appointment', 'patient_id', string='Appointments')
    nfb_form_ids = fields.One2many(
        'tarkeez.nfb_form', 'patient_id', string='NFB Forms')

    appointment_count = fields.Integer(
        string='Appointments', compute='_compute_counts', store=False)
    nfb_form_count = fields.Integer(
        string='NFB Forms', compute='_compute_counts', store=False)

    @api.depends('appointment_ids', 'nfb_form_ids')
    def _compute_counts(self):
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids)
            rec.nfb_form_count = len(rec.nfb_form_ids)

    def action_open_patient_appointments(self):
        self.ensure_one()
        action = self.env.ref('tarkeez_clinic.action_tarkeez_appointment').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id,
        }
        return action

    def action_open_patient_nfb_forms(self):
        self.ensure_one()
        action = self.env.ref('tarkeez_clinic.action_tarkeez_nfb_form').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id,
        }
        return action

