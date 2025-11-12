# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TarkeezNfbForm(models.Model):
    _name = 'tarkeez.nfb_form'
    _description = 'Tarkeez NFB Form'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one(
        'tarkeez.patient', string='Patient', required=True, ondelete='cascade')
    appointment_id = fields.Many2one(
        'tarkeez.appointment', string='Appointment',
        domain="[('patient_id', '=', patient_id)]")
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    form_type = fields.Selection([
        ('intake', 'Intake'),
        ('assessment', 'Assessment'),
        ('session', 'Session'),
        ('follow_up', 'Follow Up'),
        ('other', 'Other'),
    ], string='Form Type', default='session', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')
    attachment_id = fields.Many2one('ir.attachment', string='Attachment')

