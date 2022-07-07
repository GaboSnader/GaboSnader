# -*- coding: utf-8 -*-
# from odoo import http


# class TestMod(http.Controller):
#     @http.route('/test_mod/test_mod/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_mod/test_mod/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_mod.listing', {
#             'root': '/test_mod/test_mod',
#             'objects': http.request.env['test_mod.test_mod'].search([]),
#         })

#     @http.route('/test_mod/test_mod/objects/<model("test_mod.test_mod"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_mod.object', {
#             'object': obj
#         })
