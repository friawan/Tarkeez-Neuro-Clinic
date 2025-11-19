# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command
from babel.dates import format_date
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
    appointment_type_id = fields.Many2one('appointment.type',string="Appointment Type")

    # invoice = fields.Many2one('dental.invoice', string='invoice')
    # services_id = fields.Many2one('res.services', string='Services', domain="[('is_show', '=', True)]")

    @api.model_create_multi
    @api.returns('self')
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code("tarkeez.appointments") or _('New')
        return super(TarkeezAppointments, self).create(vals_list)

class AppointmentType(models.Model):
    _name = "appointment.type"
    _inherit = ['mail.thread']
    _description = "Appointment Type"

    name = fields.Char(string="Type Name", required=True)
    color = fields.Integer(string="Color")
    active = fields.Boolean(default=True)

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
    session_ids = fields.One2many('patient.session', 'patient_id')
    package_ids = fields.One2many('patient.package', 'patient_id', string="Packages")
    follow_up_ids = fields.One2many('tarkeez.follow.up.line', 'patient_id')
    symptom_line_ids = fields.One2many('tarkeez.symptom.line', 'patient_id')
    doctor_id = fields.Many2one('res.doctors', string='Doctor')
    patient_age = fields.Integer(string="Age", compute="_compute_age", store=True)
    birthday = fields.Date(string='Birthday')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ], string='Gender')
    handedness = fields.Selection([('left', 'Left'), ('right', 'Right'), ], string='Handedness')
    age_group = fields.Selection([('adult', 'Adult'), ('child', 'Child'), ], required=True, string='Age Group')
    code = fields.Char(readonly=True )
    date = fields.Datetime('Date', default=fields.Datetime.now)
    signature = fields.Binary(string='Signature')
    invoice_count = fields.Integer(compute="compute_invoice_count")
    package_count = fields.Integer(compute="_compute_package_count")
    appointment_count = fields.Integer(string="Appointments",compute="_compute_appointment_count")
    diagnosis = fields.Char(string="Diagnosis")
    qid = fields.Char(string="ID")
    core_symptoms = fields.Text(string='Symptoms ')
    medications = fields.Text(string='Medications or Reports?')

    def compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['account.move'].search_count([
                ('partner_id', '=', rec.partner_id.id),
                ('move_type', 'in', ['out_invoice', 'out_refund'])
            ])
    def _compute_package_count(self):
        for rec in self:
            rec.package_count = self.env['patient.package'].search_count([
                ('patient_id', '=', rec.id)
            ])
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['res.appointments'].search_count([
                ('patient_id', '=', rec.id)
            ])
    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [
                ('partner_id', '=', self.partner_id.id),
                ('move_type', 'in', ['out_invoice', 'out_refund'])
            ],
            'context': {'default_partner_id': self.partner_id.id},
        }
    def action_view_packages(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Packages',
            'res_model': 'patient.package',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
    def action_view_appointments(self):
        return {
            'name': "Appointments",
            'type': 'ir.actions.act_window',
            'res_model': 'res.appointments',
            'view_mode': 'calendar,form',
            'domain': [('patient_id', '=', self.id)],
            'context': dict(self.env.context),
        }
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
            symptoms = self.env['res.symptom'].search([('age_group', '=', patient.age_group)])
            symptoms = sorted(symptoms, key=lambda s: (s.section_id.name or '', s.name or ''))

            line_commands = []
            seq = 1
            current_section = None

            for symptom in symptoms:
                if symptom.section_id != current_section:
                    current_section = symptom.section_id
                    # Get section name from res.symptom selection
                    section_label = current_section.name if current_section else 'Unknown'                    # Add section header line
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
            if line_commands:
                patient.write({'symptom_line_ids': line_commands})
        return True

    def action_add_package(self):
        return {
            'name': 'Select Service / Package',
            'type': 'ir.actions.act_window',
            'res_model': 'patient.package.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_patient_id': self.id},
        }

class TrakeezEmployee(models.Model):
    _name = "res.employee"
    _description = 'Employee'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread']

    signature = fields.Binary(string='Signature')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True, index=True,
                                 string='Related Partner', help='Partner-related data of the user')

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
    is_package = fields.Boolean("Is Package?")
    sessions_count = fields.Integer("Number of Sessions")
    milestones = fields.Text("Milestones JSON")

class PatientPackage(models.Model):
    _name = "patient.package"
    _description = "Patient Package"
    name = fields.Char("Package Name", compute="_compute_name", store=True)
    patient_id = fields.Many2one('res.patients', string='Patient', required=True)
    service_id = fields.Many2one('res.services', string='Service/Package', required=True)
    total_sessions = fields.Integer(related='service_id.sessions_count')
    remaining_sessions = fields.Integer()
    price = fields.Float(related='service_id.price')
    installment_ids = fields.One2many('patient.package.installment', 'package_id', string='Installments')

    @api.depends('service_id')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.service_id.name if rec.service_id else ""

class PatientPackageInstallment(models.Model):
    _name = "patient.package.installment"
    _description = "Package Installment"

    package_id = fields.Many2one('patient.package', string='Package', required=True)
    session_number = fields.Integer("Session Number", required=True)
    amount = fields.Float("Amount", required=True)
    paid = fields.Boolean("Paid", default=False)
    invoice_ids = fields.One2many('account.move', 'package_id', string='Invoices')

class AccountMove(models.Model):
    _inherit = 'account.move'

    package_id = fields.Many2one('patient.package', string="Package")

class PatientSession(models.Model):
    _name = "patient.session"
    _description = "Patient Session"

    patient_id = fields.Many2one('res.patients', string='Patient', required=True)
    package_id = fields.Many2one('patient.package', string='Related Package')
    service_id = fields.Many2one('res.services', string='Service', required=True)
    session_number = fields.Integer("Session Number")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')
    date_done = fields.Datetime("Done Date")
    invoice_id = fields.Many2one('account.move', string="Invoice")

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.date_done = fields.Datetime.now()
            if rec.package_id:
                rec.package_id.remaining_sessions -= 1
                installments = rec.package_id.installment_ids.filtered(
                    lambda l: l.session_number == rec.session_number and not l.paid
                )
                for inst in installments:
                    invoice = self.env['account.move'].create({
                        'move_type': 'out_invoice',
                        'partner_id': rec.patient_id.partner_id.id,  # patient must have linked partner
                        'invoice_line_ids': [(0, 0, {
                            'name': f"Installment for session {inst.session_number}",
                            'quantity': 1,
                            'price_unit': inst.amount,
                        })],
                    })
                    invoice.action_post()
                    inst.paid = True
                    rec.invoice_id = invoice.id
            else:
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'partner_id': rec.patient_id.partner_id.id,
                    'invoice_line_ids': [(0, 0, {
                        'name': f"Single session {rec.session_number}",
                        'quantity': 1,
                        'price_unit': rec.service_id.price,
                    })],
                    'package_id': rec.package_id.id,
                })
                invoice.action_post()
                rec.invoice_id = invoice.id
        return True

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
    state = fields.Selection(selection=[('draft', 'Draft'), ('inprogress', 'Inprogress'), ('done', 'Done'), ],string='State', required=True, copy=False, tracking=True, )

    @api.onchange('paid', 'price')
    def _onchange_remaining(self):
        for rec in self:
            if rec.paid:
                rec.remaining = rec.price - rec.paid
            else:
                rec.remaining = 0.0

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
    age_group = fields.Selection([('adult', 'Adult'), ('child', 'Child'), ], required=True, string='Age Group')
    section_id = fields.Many2one('res.section',string='Section',required=True,ondelete='restrict')

class ResSection(models.Model):
    _name = "res.section"
    _inherit = ['mail.thread']
    _description = "Sections"

    name = fields.Char(string="Section", required=True)
    date = fields.Datetime('Date', default=fields.Datetime.now)

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
    attendance = fields.Selection([
        ('present', 'Yes'),
        ('absent', 'No')
    ], store=True , default=False ,string=' Yes / No ')
    notes = fields.Text(string='Notes / ملاحظات')

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

    # Prevent changing line type
    def write(self, values):
        if 'display_type' in values:
            if any(line.display_type != values.get('display_type') for line in self):
                raise UserError(
                    _("You cannot change the type of a symptom line. "
                      "Delete the line and create a new line of the proper type.")
                )
        return super().write(values)
