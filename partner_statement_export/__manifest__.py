# -*- coding: utf-8 -*-
{
    'name': 'Partner Statement Export',
    'version': '18.0.1.0.0',
    'summary': 'Export customer/vendor statements to PDF and XLSX',
    'category': 'Accounting/Reporting',
    'author': 'Custom',
    'depends': ['account', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/partner_statement_wizard_views.xml',
        'reports/partner_statement_pdf.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
}

