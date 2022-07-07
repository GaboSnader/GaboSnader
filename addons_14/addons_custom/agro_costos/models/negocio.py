# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class Negocio(models.Model):
    _name = 'costos.negocio'
    _inherit = 'mail.thread'
    _rec_name = 'negocio'
    _description = "Negocio"

    clave = fields.Char(string='Clave', required=True,index=True, track_visibility=True)
    negocio = fields.Char(string='Negocio', required=True,track_visibility=True)
    active = fields.Boolean (string="Estatus", required=False,default = True)
    _sql_constraints = [
        ('equipo_clave_uniq',
        'UNIQUE (clave)',
        'La clave del negocio debe ser unica!')]
    sucursal = fields.Many2many('stock.warehouse', string='Sucursal',track_visibility=True,required=True)
    company_id = fields.Many2one('res.company', string='Empresa',default=lambda self: self._default_company(),track_visibility=True)
    description = fields.Text(string='Descripción',track_visibility=True)
    list_sucursal = fields.Text(string='sucursal',track_visibility=True)


    @api.onchange('sucursal')
    def _onchange(self):
        acumulador = ""
        for x in self.sucursal:
            obj = x.name + " - "
            acumulador += obj
        self.list_sucursal = acumulador

    
    def _default_company(self):
        context = self._context
        _uid = self.env.user.id
        company_default = self.env['hr.employee'].search([('user_id','=',_uid)])
        return company_default.company_id.id