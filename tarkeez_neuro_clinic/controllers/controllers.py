# -*- coding: utf-8 -*-
# from odoo import http


# class TarkeezNeuroClinic(http.Controller):
#     @http.route('/tarkeez_neuro_clinic/tarkeez_neuro_clinic', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tarkeez_neuro_clinic/tarkeez_neuro_clinic/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tarkeez_neuro_clinic.listing', {
#             'root': '/tarkeez_neuro_clinic/tarkeez_neuro_clinic',
#             'objects': http.request.env['tarkeez_neuro_clinic.tarkeez_neuro_clinic'].search([]),
#         })

#     @http.route('/tarkeez_neuro_clinic/tarkeez_neuro_clinic/objects/<model("tarkeez_neuro_clinic.tarkeez_neuro_clinic"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tarkeez_neuro_clinic.object', {
#             'object': obj
#         })

