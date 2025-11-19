from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerStatementWizard(models.TransientModel):
    _name = 'partner.statement.wizard'
    _description = 'Partner Statement Wizard'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date_from = fields.Date(string='Start Date', required=True, default=lambda self: fields.Date.subtract(fields.Date.today(), months=1))
    date_to = fields.Date(string='End Date', required=True, default=fields.Date.today)
    output = fields.Selection([('pdf', 'PDF'), ('xlsx', 'Excel')], string='Output', default='pdf', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model == 'res.partner' and active_id and not res.get('partner_id'):
            res['partner_id'] = active_id
        return res

    def _get_statement_lines(self):
        self.ensure_one()
        aml = self.env['account.move.line']
        # Include both receivable and payable accounts in a single statement
        account_types = ['asset_receivable', 'liability_payable']
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('parent_state', '=', 'posted'),
            ('account_id.account_type', 'in', account_types),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        lines = aml.search(domain, order='date, move_name, id')

        # opening balance before date_from
        opening_domain = [
            ('partner_id', '=', self.partner_id.id),
            ('parent_state', '=', 'posted'),
            ('account_id.account_type', 'in', account_types),
            ('date', '<', self.date_from),
        ]
        # Opening balance: receivable balances add, payable balances subtract
        opening_moves = aml.search(opening_domain)
        opening = 0.0
        for m in opening_moves:
            if m.account_id.account_type == 'asset_receivable':
                opening += (m.balance or 0.0)
            else:  # liability_payable
                opening -= (m.balance or 0.0)
        balance = opening
        rows = []
        for l in lines:
            # Natural presentation: show Dr/Cr as posted; compute running
            # balance with receivable adding and payable subtracting.
            debit = l.debit or 0.0
            credit = l.credit or 0.0
            sign = 1 if l.account_id.account_type == 'asset_receivable' else -1
            balance += sign * ((l.debit or 0.0) - (l.credit or 0.0))
            move = l.move_id
            policy_no = getattr(move, 'policy_number_display', False) or ''
            debit_note_no = getattr(move, 'insurer_debit_note_number_display', False) or ''
            credit_note_no = getattr(move, 'insurer_credit_note_number_display', False) or ''
            # unified label / reference
            label = ''
            if hasattr(move, '_get_insurance_unified_label'):
                try:
                    label = move._get_insurance_unified_label()
                except Exception:
                    label = ''
            reference = move.ref or move.payment_reference or label
            rows.append({
                'date': l.date,
                'move': l.move_id.name or l.move_name,
                'journal': l.journal_id.display_name,
                'policy': policy_no,
                'debit_note': debit_note_no,
                'credit_note': credit_note_no,
                'reference': reference,
                'label': label,
                'debit': debit,
                'credit': credit,
                'balance': balance,
            })
        return opening, rows

    def action_print(self):
        self.ensure_one()
        data = {
            'partner_id': self.partner_id.id,
            'partner_name': self.partner_id.display_name,
            'date_from': self.date_from.isoformat(),
            'date_to': self.date_to.isoformat(),
        }
        if self.output == 'pdf':
            # Try to resolve PDF report by external id, then fallback to search, then create if missing
            try:
                report = self.env.ref('partner_statement_export.report_partner_statement_pdf')
            except ValueError:
                report = self.env['ir.actions.report'].search([
                    ('report_type', '=', 'qweb-pdf'),
                    ('model', '=', 'partner.statement.wizard'),
                    ('report_name', '=', 'partner_statement_export.statement_pdf')
                ], limit=1)
                if not report:
                    report = self.env['ir.actions.report'].sudo().create({
                        'name': 'Partner Statement',
                        'model': 'partner.statement.wizard',
                        'report_type': 'qweb-pdf',
                        'report_name': 'partner_statement_export.statement_pdf',
                        'print_report_name': "'Statement - %s' % (object.partner_id.display_name)",
                    })
            return report.report_action(self, data=data)
        # XLSX with fallback if the external id isn't loaded yet
        try:
            report = self.env.ref('partner_statement_export.report_partner_statement_xlsx')
        except ValueError:
            report = self.env['ir.actions.report'].search([
                ('report_type', '=', 'xlsx'),
                ('model', '=', 'partner.statement.wizard'),
                ('report_name', '=', 'partner_statement_export.statement_xlsx')
            ], limit=1)
            if not report:
                # Create the report action dynamically if not loaded yet
                report = self.env['ir.actions.report'].sudo().create({
                    'name': 'Partner Statement (XLSX)',
                    'model': 'partner.statement.wizard',
                    'report_type': 'xlsx',
                    'report_name': 'partner_statement_export.statement_xlsx',
                    'print_report_name': "'Statement - %s' % (object.partner_id.display_name)",
                })
            if not report:
                raise UserError(_('The XLSX report is not available. Please upgrade the module or install report_xlsx.'))
        return report.report_action(self, data=data)
