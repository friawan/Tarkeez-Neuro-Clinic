# -*- coding: utf-8 -*-
{
    'name': "Tarkeez Neuro Clinic",
    'summary': "Manage patients, therapists, and neurofeedback sessions",
    'description': """
        A complete system for managing Tarkeez Neurofeedback Clinic operations, 
        including patient registration, session tracking, therapist management, 
        and progress reports.
    """,

    'author': "Ouro Technology",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Healthcare Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','web','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'reports/trakeez_reports.xml',
        'views/templates.xml',
        'wizard/package.xml',
        'data/ir_sequence.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'tarkeez_neuro_clinic/static/src/css/style.css',
        ],
        "web.report_assets_pdf": [
             'tarkeez_neuro_clinic/static/src/css/style.css',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

