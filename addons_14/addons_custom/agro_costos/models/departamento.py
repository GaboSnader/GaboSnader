# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

class Departamento(models.Model):
    _name = 'costos.departamento'
    _rec_name = 'departamento'
    _inherit = 'mail.thread'
    
    clave = fields.Char(string='Clave', store=True,track_visibility=True)
    departamento = fields.Char(string='Departamento', store=True,track_visibility=True)
    active = fields.Boolean (string="Estatus", required=False, default=True)
    sucursal = fields.Many2many('stock.warehouse',string='Sucursal',track_visibility=True,required=True)
    company_id = fields.Many2one('res.company',string='Empresa',default=lambda self: self._default_company(),track_visibility='onchange')
    description = fields.Text(string='Descripción',track_visibility=True)
    list_sucursal = fields.Text(string='sucursal',track_visibility=True)


    @api.onchange('sucursal')
    def _onchange(self):
        acumulador = ""
        for x in self.sucursal:
            obj = x.name + " - "
            acumulador += obj
        self.list_sucursal = acumulador
    
    def name_get(self):
        res = []
        for discount in self:
            name = discount.clave
            res.append((discount.id, name))
        return res
    
    
    def _default_company(self):
        context = self._context
        _uid = self.env.user.id
        company_default = self.env['hr.employee'].search([('user_id','=',_uid)])
        return company_default.company_id.id
