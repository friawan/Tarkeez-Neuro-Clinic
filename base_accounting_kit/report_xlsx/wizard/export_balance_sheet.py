from odoo import models
import openpyxl
from openpyxl.styles import Font
from odoo.http import request
from odoo.tools.misc import xlsxwriter

class ExportBalanceSheet(models.TransientModel):
    _name = 'export.balance.sheet.wizard'
    _description = 'Export Balance Sheet to Excel'

    def export_excel(self):
        # تهيئة ملف Excel
        from io import BytesIO
        import base64

        output = BytesIO()
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Balance Sheet"
        sheet.append(["Report", "Value"])
        sheet.append(["Assets", 10000])
        sheet.append(["Liabilities", 5000])
        workbook.save(output)
        output.seek(0)

        # حفظ كمرفق وتنزيله
        attachment = self.env['ir.attachment'].create({
            'name': 'balance_sheet.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
        })
        download_url = '/web/content/%s?download=true' % attachment.id
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'self',
        }
