# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command
from  babel.dates import format_date
import locale


class TarkeezAppointments(models.Model):
    _name = 'res.appointments'
    _description = 'Appointments'
    _inherit = ['mail.thread']

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('in_clinic', 'In Clinic'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'), ],
        string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')
    name = fields.Char(readonly=True, )
    start_date = fields.Datetime('Start Date', required=True)
    end_date = fields.Datetime('End Date', required=True)
    patient_id = fields.Many2one('res.patients', required=True, ondelete='restrict', string='Patients')
    employee_id = fields.Many2one('res.employee', ondelete='restrict', string='Employee')
    doctor_id = fields.Many2one('res.doctors', required=True, ondelete='restrict', string='Doctors')
    is_collect = fields.Boolean(string='Examination Fees')
    # invoice = fields.Many2one('dental.invoice', string='invoice')
    # services_id = fields.Many2one('res.services', string='Services', domain="[('is_show', '=', True)]")

    @api.model_create_multi
    @api.returns('self')
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code("tarkeez.appointments") or _('New')
        return super(TarkeezAppointments, self).create(vals_list)
class TrakeezDoctors(models.Model):
    _name = "res.doctors"
    _description = 'Doctors'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread']

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True, index=True,
                                 string='Related Partner', help='Partner-related data of the user')
    signature = fields.Binary(string='Signature')
class TrakeezPatients(models.Model):
    _name = "res.patients"
    _description = 'Patients'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread']

    sequence = fields.Char()
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True, index=True,
                                 string='Related Partner', help='Partner-related data of the user')
    services_ids = fields.One2many('res.services.line', 'patient_id')
    follow_up_ids = fields.One2many('tarkeez.follow.up.line', 'patient_id')
    symptom_line_ids = fields.One2many('tarkeez.symptom.line', 'patient_id')
    doctor_id = fields.Many2one('res.doctors', string='Doctor')
    patient_age = fields.Integer(string="Age", compute="_compute_age", store=True)
    birthday = fields.Date(string='Birthday')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ], string='Gender')
    age_group = fields.Selection([('adult', 'Adult'), ('child', 'Child'),],required=True, string='Age Group')
    code = fields.Char(readonly=True, )
    date = fields.Datetime('Date', default=fields.Datetime.now)
    signature = fields.Binary(string='Signature')
    invoice = fields.Many2one('dental.invoice', string='invoice')
    diagnosis = fields.Char(string="Diagnosis")
    qid = fields.Char(string="QID")

    core_symptoms = fields.Text(string='Symptoms for Kid?  ')
    medications = fields.Text(string='Medications or Reports?')

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('New')) == _('New'):
                vals['code'] = self.env['ir.sequence'].next_by_code("tarkeez.patient") or _('New')
        return super(TrakeezPatients, self).create(vals_list)

    @api.depends('birthday')
    def _compute_age(self):
        for rec in self:
            if rec.birthday:
                today = date.today()
                rec.patient_age = today.year - rec.birthday.year - (
                        (today.month, today.day) < (rec.birthday.month, rec.birthday.day)
                )

            else:
                rec.patient_age = 0

    def action_regenerate_symptoms(self):
        for patient in self:
            if not patient.age_group:
                continue

            # Delete existing symptom lines
            patient.symptom_line_ids.unlink()

            # Get symptoms for this patient, ordered by section and name
            symptoms = self.env['res.symptom'].search(
                [('age_group', '=', patient.age_group)],
                order='section, name'
            )

            line_commands = []
            seq = 1
            current_section = None

            for symptom in symptoms:
                if symptom.section != current_section:
                    current_section = symptom.section
                    # Get section name from res.symptom selection
                    section_label = dict(self.env['res.symptom']._fields['section'].selection).get(current_section)
                    # Add section header line
                    line_commands.append((0, 0, {
                        'name': section_label,
                        'display_type': 'line_section',
                        'sequence': seq,
                    }))
                    seq += 1

                # Add symptom line
                line_commands.append((0, 0, {
                    'name': symptom.name,
                    'display_type': False,
                    'sequence': seq,
                }))
                seq += 1

            print(line_commands,22222222222222222222222222)

            if line_commands:
                patient.write({'symptom_line_ids': line_commands})
        return True

    # invoice = fields.Many2one('dental.invoice', string='invoice')
class TrakeezEmployee(models.Model):
    _name = "res.employee"
    _description = 'Employee'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread']

    signature = fields.Binary(string='Signature')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True, index=True,string='Related Partner', help='Partner-related data of the user')
class Trakeezservices(models.Model):
    _name = "res.services"
    _description = 'Services'
    _inherit = ['mail.thread']
    name = fields.Char(translate=True)
    sequence = fields.Char()
    date = fields.Datetime('Date', default=fields.Datetime.now)
    description = fields.Char('description', translate=True)
    image = fields.Image('image')
    is_puplic_list = fields.Boolean(string='Puplic List')
    price = fields.Float('Price', digits=(16, 1))  # Float because we add 0.1 to avoid zero Frequency issue
class TrakeezservicesLine(models.Model):
    _name = "res.services.line"
    _description = 'Services line'

    patient_id = fields.Many2one('res.patients', string='Services Partner')
    services_id = fields.Many2one('res.services', string='Services')
    date = fields.Datetime('Date', default=fields.Datetime.now)
    description = fields.Char('description', related='services_id.description')
    price = fields.Float('Price', digits=(16, 1), related='services_id.price')
    paid = fields.Float('Paid', digits=(16, 1), )
    remaining = fields.Float('Remaining', digits=(16, 1), )
    bool_field = fields.Boolean('checked', default=False)

    state = fields.Selection(selection=[('draft', 'Draft'), ('inprogress', 'Inprogress'), ('done', 'Done'), ],
                             string='State', required=True, copy=False, tracking=True, )

    @api.onchange('paid', 'price')
    def _onchange_remaining(self):
        for rec in self:
            if rec.paid:
                rec.remaining = rec.price - rec.paid
            else:
                rec.remaining = 0.0

    # def add_to_invoice(self):
    #     for rec in self:
    #         if rec.patient_id.invoice:
    #             vals_list = {
    #                 'services_id': rec.services_id.id,
    #                 'section': rec.section,
    #                 'state': rec.state,
    #                 'price': rec.price,
    #                 'paid': rec.paid,
    #                 'remaining': rec.remaining,
    #                 'line_id': rec.patient_id.invoice.id,
    #             }

                # post = self.env['dental.invoice.line'].sudo().create(vals_list)
                # self.bool_field = True
                # if post:
                #     return {
                #         'type': 'ir.actions.client',
                #         'tag': 'display_notification',
                #         'params': {
                #             'title': _("Hello DR"),
                #             'type': 'info',
                #             'message': _("The service '%s' has been added to the invoice.") % (rec.services_id.name),
                #             'sticky': True,
                #         },
                #     }
class TarkeezFollowUpLine(models.Model):
    _name = 'tarkeez.follow.up.line'
    _description = 'Tarkeez Follow Up line'
    _order = 'date desc, id'
    patient_id = fields.Many2one('res.patients', string='Services Partner')
    protolused = fields.Char(string="Protol used")
    observation = fields.Text(string="CLINICIAN Observation")
    parent_feedback = fields.Text(string="Parent Feedback")
    date = fields.Date(string="Date", default=fields.Date.context_today)
    notes = fields.Text(string="Notes")

class TrakeezSymptom(models.Model):
    _name = "res.symptom"
    _inherit = ['mail.thread']
    _description = 'Symptom list'

    name = fields.Char(translate=True)
    date = fields.Datetime('Date', default=fields.Datetime.now)
    age_group = fields.Selection([('adult', 'Adult'), ('child', 'Child'),],required=True, string='Age Group')
    section = fields.Selection([
        ('1', 'Group 1 – Self-Competence'),
        ('2', 'Group 2 – Emotional Competence'),
        ('3', 'Group 3 – Social Competence'),
        ('4', 'Group 4 – Physical Development'),
        ('5', 'Group 5 – Cognitive Development'),
        ('6', 'Group 6 – Spoken Language Development'),
    ],required=True, string='Section')


class TarkeezSymptomLine(models.Model):
    _name = 'tarkeez.symptom.line'
    _description = 'Symptom Line'
    _order = 'id'
    patient_id = fields.Many2one('res.patients', string='Services Partner')
    sequence = fields.Integer(string='Sequence', default=10)

    # Use display_type instead of is_section
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note"),
    ], default=False)

    name = fields.Char(string='Description')
    present = fields.Boolean(string='Yes / نعم')
    absent = fields.Boolean(string='No / لا')
    notes = fields.Text(string='Notes / ملاحظات')

    # ------------------------------
    # Override create to blank fields for section/note lines
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('display_type', self.default_get(['display_type'])['display_type']):
                vals.update({
                    'present': False,
                    'absent': False,
                    'notes': False,
                })
            return super().create(vals_list)

    # ------------------------------
    # Prevent changing line type
    def write(self, values):
        if 'display_type' in values:
            if any(line.display_type != values.get('display_type') for line in self):
                raise UserError(
                    _("You cannot change the type of a symptom line. "
                      "Delete the line and create a new line of the proper type.")
                )
        return super().write(values)