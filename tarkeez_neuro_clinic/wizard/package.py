from odoo import models, fields, api
import json
class PatientPackageWizard(models.TransientModel):
    _name = 'patient.package.wizard'
    _description = 'Wizard to add Package or Session'

    patient_id = fields.Many2one('res.patients', string='Patient', required=True)
    service_id = fields.Many2one('res.services', string='Service', required=True)
    is_package = fields.Boolean(string='Is Package?', related='service_id.is_package', readonly=True)

    def action_confirm(self):
        """Create Package or Session based on selection"""
        self.ensure_one()
        if self.is_package:
            # Create patient package
            package = self.env['patient.package'].create({
                'patient_id': self.patient_id.id,
                'service_id': self.service_id.id,
                'total_sessions': self.service_id.sessions_count,
                'remaining_sessions': self.service_id.sessions_count,
                'price': self.service_id.price,
            })
            # Create sessions for the package
            for i in range(1, self.service_id.sessions_count + 1):
                self.env['patient.session'].create({
                    'patient_id': self.patient_id.id,
                    'package_id': package.id,
                    'service_id': self.service_id.id,
                    'session_number': i,
                    'state': 'draft',
                })
            # Optionally create installments based on milestones
            milestones_text = self.service_id.milestones or '[]'
            try:
                milestones = json.loads(milestones_text)
                if isinstance(milestones, dict):
                    milestones = [milestones]
                if not isinstance(milestones, list):
                    milestones = []
            except Exception:
                milestones = []
            for m in milestones:
                self.env['patient.package.installment'].create({
                    'package_id': package.id,
                    'session_number': m.get('session'),
                    'amount': m.get('amount', 0.0),
                    'paid': False,
                })
        else:
            # Create single session
            self.env['patient.session'].create({
                'patient_id': self.patient_id.id,
                'service_id': self.service_id.id,
                'session_number': 1,
                'state': 'draft',
            })

        return {'type': 'ir.actions.act_window_close'}
