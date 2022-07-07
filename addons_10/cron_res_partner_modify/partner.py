# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, UserError

class partner_modify(models.Model):
    _name = 'partner.modify'
    _description = 'Modificaciones de Res Partner'

    name = fields.Char('Nombre')
    zip = fields.Char('Codigo Postal')
    country_id = fields.Many2one('res.country', 'Pais')
    email = fields.Char('Correo Electronico')
    vat = fields.Char('RFC')
    ref = fields.Char('Referencia Interna')
    parent_id = fields.Many2one('res.partner', 'Compañia')
    ref_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    phone = fields.Char('Teléfono')
    modify = fields.Boolean('Modificar')
    delete = fields.Boolean('Eliminar')

    @api.model
    def _cron_partner_modify(self, ids=None):
        partner_obj = self.env['res.partner']
        modify_obj = self.env['partner.modify']
        modify_create = modify_obj.search([('ref_id','=',False)])
        modify_update = modify_obj.search([('modify','=',True)])
        modify_delete = modify_obj.search([('delete','=',True)])
        print "######## MODIFY CREATE >>>>>> ", modify_create
        print "########## MODIFY UPDATE >>>>>> ", modify_update
        print "############ MODIFY DELETE >>>>>> ",modify_delete
        if modify_create:
            for new in modify_create:
                partner_vals = {
                    'name': new.name,
                    'zip': new.zip,
                    'country_id': new.country_id.id,
                    'email': new.email,
                    'vat': new.vat,
                    'ref': new.ref,
                    'parent_id': new.parent_id.id,
                    'phone': new.phone,
                    }
                new.ref_id = partner_obj.create(partner_vals)
        elif modify_update:
            for up in modify_update:
                partner_vals = {
                    'name': up.name,
                    'zip': up.zip,
                    'country_id': up.country_id.id,
                    'email': up.email,
                    'vat': up.vat,
                    'ref': up.ref,
                    'parent_id': up.parent_id.id,
                    'phone': up.phone,
                    }
                up.ref_id.update(partner_vals)
                up.modify = False
        elif modify_delete:
            for dlt in modify_delete:
                dlt.ref_id.toggle_active()
                dlt.delete = False
        return True

    _order = 'name'
    _defaults = {
        'active': True,
       }