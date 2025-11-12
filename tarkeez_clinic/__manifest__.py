# -*- coding: utf-8 -*-
{
    'name': 'Tarkeez Neuro Clinic',
    'summary': 'Manage patients, appointments, and NFB forms for a neurofeedback clinic.',
    'version': '1.0.0',
    'category': 'Healthcare',
    'license': 'LGPL-3',
    'author': 'Tarkeez',
    'website': '',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/patient_views.xml',
        'views/appointment_views.xml',
        'views/nfb_form_views.xml',
        'views/symptom_checklist_kids_views.xml',
        'report/symptom_checklist_kids_action.xml',
        'report/symptom_checklist_kids_report.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
}
