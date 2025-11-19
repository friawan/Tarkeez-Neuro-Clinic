from odoo import models


class ReportPartnerStatementXlsx(models.AbstractModel):
    _name = 'report.partner_statement_export.statement_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Partner Statement XLSX'

    def generate_xlsx_report(self, workbook, data, partners):
        wizard = partners and partners[0] if partners else None
        if wizard and wizard._name == 'partner.statement.wizard':
            opening, rows = wizard._get_statement_lines()
            partner_name = wizard.partner_id.display_name
            date_from = wizard.date_from
            date_to = wizard.date_to
        else:
            partner = self.env['res.partner'].browse(data.get('partner_id'))
            tmp = self.env['partner.statement.wizard'].new({
                'partner_id': partner.id,
                'date_from': data.get('date_from'),
                'date_to': data.get('date_to'),
            })
            opening, rows = tmp._get_statement_lines()
            partner_name = partner.display_name
            date_from = data.get('date_from')
            date_to = data.get('date_to')

        sheet = workbook.add_worksheet('Statement')
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})

        sheet.write(0, 0, 'Partner Statement', bold)
        sheet.write(1, 0, 'Partner:')
        sheet.write(1, 1, partner_name)
        sheet.write(2, 0, 'Period:')
        sheet.write(2, 1, f"{date_from} - {date_to}")
        sheet.write(3, 0, 'Opening Balance:')
        sheet.write_number(3, 1, opening, money)

        headers = ['Date', 'Move', 'Journal', 'Reference', 'Policy', 'Debit Note', 'Credit Note', 'Debit', 'Credit', 'Balance']
        for col, h in enumerate(headers):
            sheet.write(5, col, h, bold)

        row = 6
        for l in rows:
            sheet.write(row, 0, str(l['date']))
            sheet.write(row, 1, l['move'] or '')
            sheet.write(row, 2, l['journal'] or '')
            sheet.write(row, 3, l.get('reference') or '')
            sheet.write(row, 4, l.get('policy') or '')
            sheet.write(row, 5, l.get('debit_note') or '')
            sheet.write(row, 6, l.get('credit_note') or '')
            sheet.write_number(row, 7, l['debit'] or 0.0, money)
            sheet.write_number(row, 8, l['credit'] or 0.0, money)
            sheet.write_number(row, 9, l['balance'] or 0.0, money)
            row += 1
        # Totals row
        total_debit = sum(r['debit'] or 0.0 for r in rows)
        total_credit = sum(r['credit'] or 0.0 for r in rows)
        closing = rows[-1]['balance'] if rows else opening
        sheet.write(row, 0, '')
        sheet.write(row, 1, '')
        sheet.write(row, 2, 'Totals', bold)
        sheet.write(row, 3, '')
        sheet.write(row, 4, '')
        sheet.write(row, 5, '')
        sheet.write(row, 6, '')
        sheet.write_number(row, 7, total_debit, money)
        sheet.write_number(row, 8, total_credit, money)
        sheet.write_number(row, 9, closing, money)

        # Nice widths
        sheet.set_column(0, 0, 12)
        sheet.set_column(1, 1, 22)
        sheet.set_column(2, 2, 18)
        sheet.set_column(3, 6, 18)
        sheet.set_column(7, 9, 14)
