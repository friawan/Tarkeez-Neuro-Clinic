# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


SYMPTOM_GROUPS_KIDS = [
    (
        'Group 1 – Self-Competence (الرعاية الذاتية)',
        [
            ('يستطيع الابتعاد عن الوالدين بسهولة', 'Can separate from caregivers without difficulty'),
            ('يستطيع التواصل مع الآخرين بأمان', 'Develops a secure attachment with caregiver'),
            ('يستطيع اختيار الألعاب بدون مساعدة الأهل', 'Makes activity choices without caregivers’ help'),
            ('يحصل على حقه بنفسه', 'Stands up for own rights'),
        ],
    ),
    (
        'Group 2 – Emotional Competence (القدرة الانفعالية)',
        [
            ('يستطيع التعبير عن مشاعره بطريقة مناسبة', 'Shows stressful feelings in an appropriate manner'),
            ('يعبّر عن غضبه بالكلمات أكثر من السلوك السلبي', 'Shows anger in words rather than in negative actions'),
            ('يتسم بالهدوء في المواقف المخيفة', 'Calms in frightening situations'),
            ('يظهر مشاعر الحب تجاه الآخرين', 'Shows affection and love towards others'),
            ('يُظهر اهتمامًا بالأنشطة الجديدة', 'Shows interest in new activities'),
            ('يبتسم ويبدو سعيدًا معظم الوقت', 'Smiles or seems happy most of the time'),
        ],
    ),
    (
        'Group 3 – Social Competence (القدرة الاجتماعية)',
        [
            ('يلعب لوحده مع ألعابه', 'Plays by self with own materials'),
            ('يلعب بشكل متوازٍ مع الآخرين بنفس الألعاب', 'Plays parallel with others with similar toys'),
            ('يلعب مع الآخرين بشكل جماعي', 'Plays with others in group play'),
            ('يكون صداقات مع أطفال آخرين', 'Makes friends with other children'),
            ('يسوّي الخلافات أثناء اللعب بطريقة إيجابية', 'Resolves play conflicts in a positive manner'),
        ],
    ),
    (
        'Group 4 – Physical Development (التطور الحركي)',
        [
            ('يستطيع الركض بسرعة وسيطرة مناسبة', 'Runs with controlled speed and direction'),
            ('يستطيع التسلق صعودًا ونزولًا بسهولة', 'Climbs up and down with ease'),
            ('يرمي ويمسك ويركل الكرة', 'Throws, catches, and kicks the ball'),
            ('يستطيع لف الأغطية والمقابض', 'Turns lids and knobs'),
            ('يلتقط الأشياء ويرتبها بدقة', 'Picks up and inserts objects with dexterity'),
            ('يستخدم الأدوات مثل المطرقة والمقص بسهولة وتحكم', 'Uses tools (hammer, scissors) with control'),
        ],
    ),
    (
        'Group 5 – Cognitive Development (التطور العقلي)',
        [
            ('يصنف الأشياء حسب الشكل واللون والحجم', 'Classifies objects by shape, color, and size'),
            ('ينظم الأشياء بترتيب وتسلسل', 'Places objects in sequence or series'),
            ('يستطيع العد بشكل تلقائي', 'Counts by rote'),
            ('يربط العدد بالرقم بشكل صحيح', 'Displays one-to-one correspondence with numbers'),
            ('يحل المشكلات باستخدام أشياء محسوسة', 'Solves problems with concrete objects'),
        ],
    ),
    (
        'Group 6 – Spoken Language Development (تطور اللغة المحكية)',
        [
            ('يسمع لكنه لا يتكلم', 'Listens but does not speak'),
            ('يجيب بكلمة واحدة أو جملة قصيرة', 'Gives single-word or short-phrase responses'),
            ('يشارك في الحوار', 'Takes part in conversation'),
            ('يتحدث بجمل طويلة ويستطرد', 'Speaks in expanded sentences'),
            ('يطرح أسئلة', 'Asks questions'),
            ('يستطيع أن يسرد قصة', 'Can tell a story'),
            ('يسرد حادثة شاهدها', 'Narrates an incident'),
        ],
    ),
]


class TarkeezSymptomChecklistKids(models.Model):
    _name = 'tarkeez.symptom_checklist_kids'
    _description = 'Symptom Checklist (Kids)'
    _order = 'date desc, id desc'

    patient_id = fields.Many2one('tarkeez.patient', string='Patient', required=True, ondelete='cascade')
    appointment_id = fields.Many2one(
        'tarkeez.appointment', string='Appointment',
        domain="[('patient_id', '=', patient_id)]")
    date = fields.Date(string='Session Date', default=fields.Date.context_today)

    item_ids = fields.One2many(
        'tarkeez.symptom_line_kids', 'checklist_id', string='Symptoms')

    core_symptoms = fields.Text(string='Core Symptoms for Kid? / الأعراض الأساسية للطفل؟')
    medications = fields.Text(string='Any Medications or Reports? / أي أدوية أو تقارير؟')
    signature = fields.Binary(string='Signature / التوقيع')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list):
            # Only auto-populate if no items provided
            if not vals.get('item_ids') and not rec.item_ids:
                line_commands = []
                seq = 1
                for group_name, items in SYMPTOM_GROUPS_KIDS:
                    # section header
                    line_commands.append((0, 0, {
                        'sequence': seq,
                        'display_type': 'line_section',
                        'name': group_name,
                        'domain': group_name,
                    }))
                    seq += 1
                    for ar, en in items:
                        line_commands.append((0, 0, {
                            'sequence': seq,
                            'domain': group_name,
                            'symptom_ar': ar,
                            'symptom_en': en,
                        }))
                        seq += 1
                rec.write({'item_ids': line_commands})
        return records

    def action_regenerate_symptoms(self):
        for rec in self:
            rec.item_ids.unlink()
            line_commands = []
            seq = 1
            for group_name, items in SYMPTOM_GROUPS_KIDS:
                line_commands.append((0, 0, {
                    'sequence': seq,
                    'display_type': 'line_section',
                    'name': group_name,
                    'domain': group_name,
                }))
                seq += 1
                for ar, en in items:
                    line_commands.append((0, 0, {
                        'sequence': seq,
                        'domain': group_name,
                        'symptom_ar': ar,
                        'symptom_en': en,
                    }))
                    seq += 1
            rec.write({'item_ids': line_commands})
        return True

    def action_print_checklist(self):
        self.ensure_one()
        report = None
        try:
            report = self.env.ref('tarkeez_clinic.report_symptom_checklist_kids')
        except ValueError:
            # Fallback by technical name if XML-ID not yet available
            report = self.env['ir.actions.report']._get_report_from_name('tarkeez_clinic.symptom_checklist_kids_template')
        if not report:
            # As a last resort, create the report action dynamically
            report = self.env['ir.actions.report'].create({
                'name': 'Kids Symptom Checklist',
                'model': 'tarkeez.symptom_checklist_kids',
                'report_name': 'tarkeez_clinic.symptom_checklist_kids_template',
                'report_type': 'qweb-pdf',
                'print_report_name': "'Kids Checklist - %s' % (object.patient_id.name or '')",
            })
        return report.report_action(self)

    def action_fix_lines(self):
        for rec in self:
            for line in rec.item_ids:
                # Title row if no symptom text; otherwise normal symptom row
                if (not line.symptom_ar and not line.symptom_en) and (line.name or line.domain):
                    line.display_type = 'line_section'
                else:
                    line.display_type = False
        return True


class TarkeezSymptomLineKids(models.Model):
    _name = 'tarkeez.symptom_line_kids'
    _description = 'Symptom Line (Kids)'
    _order = 'sequence, id'

    checklist_id = fields.Many2one(
        'tarkeez.symptom_checklist_kids', string='Checklist', ondelete='cascade', required=True)
    sequence = fields.Integer(default=10)
    display_type = fields.Selection([
        ('line_section', 'Section'),
    ], default=False, help='Technical field for section headers')
    name = fields.Char(string='Section Title')
    domain = fields.Char(string='Category / Domain')
    symptom_ar = fields.Char(string='Symptom (AR)')
    symptom_en = fields.Char(string='Symptom (EN)')
    symptom_bilingual = fields.Char(string='Symptom', compute='_compute_symptom_bilingual', store=True)
    section_title = fields.Char(string='Section Title', compute='_compute_section_title', store=False)
    present = fields.Boolean(string='Yes / نعم')
    absent = fields.Boolean(string='No / لا')
    notes = fields.Text(string='Notes / ملاحظات')

    row_label = fields.Char(string='Symptom / Section', compute='_compute_row_label', store=True)

    @api.depends('symptom_ar', 'symptom_en')
    def _compute_symptom_bilingual(self):
        for rec in self:
            if rec.symptom_ar and rec.symptom_en:
                rec.symptom_bilingual = f"{rec.symptom_ar} | {rec.symptom_en}"
            else:
                rec.symptom_bilingual = rec.symptom_ar or rec.symptom_en or ''

    @api.depends('display_type', 'name', 'symptom_ar', 'symptom_en')
    def _compute_row_label(self):
        for rec in self:
            if rec.display_type == 'line_section':
                rec.row_label = rec.name or rec.domain or ''
            else:
                en = rec.symptom_en or ''
                rec.row_label = (rec.symptom_ar or '') + ((' | ' + en) if en else '')

    @api.depends('name', 'domain')
    def _compute_section_title(self):
        for rec in self:
            rec.section_title = rec.name or rec.domain or ''

    @api.onchange('present')
    def _onchange_present(self):
        for rec in self:
            if rec.present:
                rec.absent = False

    @api.onchange('absent')
    def _onchange_absent(self):
        for rec in self:
            if rec.absent:
                rec.present = False
