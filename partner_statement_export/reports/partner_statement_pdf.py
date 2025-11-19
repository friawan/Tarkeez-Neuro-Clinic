from odoo import api, models


class ReportPartnerStatementPDF(models.AbstractModel):
    _name = 'report.partner_statement_export.statement_pdf'
    _description = 'Partner Statement PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['partner.statement.wizard'].browse(docids) if docids else None
        # When called via report_action on wizard, use that wizard; otherwise, reconstruct from data
        if wizard and wizard.exists():
            opening, rows = wizard._get_statement_lines()
            total_debit = sum(r['debit'] for r in rows)
            total_credit = sum(r['credit'] for r in rows)
            closing = rows[-1]['balance'] if rows else opening
            return {
                'doc_ids': [wizard.id],
                'doc_model': 'partner.statement.wizard',
                'doc': wizard,
                'opening': opening,
                'lines': rows,
                'total_debit': total_debit,
                'total_credit': total_credit,
                'closing': closing,
            }
        # fallback for data call
        partner = self.env['res.partner'].browse(data.get('partner_id'))
        tmp = self.env['partner.statement.wizard'].new({
            'partner_id': partner.id,
            'date_from': data.get('date_from'),
            'date_to': data.get('date_to'),
        })
        opening, rows = tmp._get_statement_lines()
        total_debit = sum(r['debit'] for r in rows)
        total_credit = sum(r['credit'] for r in rows)
        closing = rows[-1]['balance'] if rows else opening
        return {
            'doc_ids': [],
            'doc_model': 'partner.statement.wizard',
            'doc': tmp,
            'opening': opening,
            'lines': rows,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'closing': closing,
        }
