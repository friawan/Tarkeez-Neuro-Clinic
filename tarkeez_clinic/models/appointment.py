# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TarkeezAppointment(models.Model):
    _name = 'tarkeez.appointment'
    _description = 'Tarkeez Appointment'
    _order = 'date_start desc'

    patient_id = fields.Many2one(
        'tarkeez.patient', string='Patient', required=True, ondelete='cascade')
    practitioner_id = fields.Many2one(
        'res.users', string='Practitioner', help='Assigned practitioner')
    date_start = fields.Datetime(string='Start', required=True)
    date_end = fields.Datetime(string='End')
    session_type = fields.Selection([
        ('assessment', 'Assessment'),
        ('training', 'Training'),
        ('consultation', 'Consultation'),
        ('other', 'Other'),
    ], string='Session Type', default='training')
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('arrived', 'Arrived'),
        ('in_session', 'In Session'),
        ('done', 'Done'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='scheduled', tracking=False)
    notes = fields.Text(string='Notes')

    def action_arrived(self):
        self.write({'state': 'arrived'})

    def action_in_session(self):
        self.write({'state': 'in_session'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_no_show(self):
        self.write({'state': 'no_show'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

