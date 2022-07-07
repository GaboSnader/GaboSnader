# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, UserError

class partner_modify(models.TransientModel):
    _name = 'create.partner.modify'
    _description = 'Modificaciones de Res Partner'

    name = fields.Char('Nombre')
    code = fields.Char('Codigo Postal')
    country_id = fields.Many2one('res.country', 'Pais')
    email = fields.Char('Correo Electronico')
    vat = fields.Char('RFC')
    ref = fields.Char('Referencia Interna')
    parent_id = fields.Many2one('res.partner', 'Compañia')
    ref_id = fields.Many2one('res.partner', 'Partner')
    phone = fields.Char('Teléfono')
    create = fields.Boolean('Creacion', default=True)
    modify = fields.Boolean('Modificar')
    delete = fields.Boolean('Eliminar')

