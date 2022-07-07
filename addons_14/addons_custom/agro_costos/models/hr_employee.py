# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sucursal = fields.Many2one('stock.warehouse',string='Sucursal',default=lambda self:self.env.user.sucursal.id)
    equipo = fields.Many2one('costos.equipo',string='Equipo',default=lambda self:self.env.user.equipo.id)
    negocio = fields.Many2one('costos.negocio',string='Negocio',default=lambda self:self.env.user.area.id)
    area = fields.Many2one('costos.area',string='Area',default=lambda self:self.env.user.department.id)
    department = fields.Many2one('costos.departamento',string='Departamento',default=lambda self:self.env.user.equipo.id)
    tipo_operacion = fields.Many2one('costos.tipo_operacion',string='Tipo de Operación',default=lambda self:self.env.user.tipo_operacion.id)

    #si se cambia la sucursal se limpian los campos area y departamento
    @api.onchange('sucursal')
    def _blank_fields(self):
        if self.sucursal.id not in self.area.sucursal.ids:
            self.area = ''
        if self.sucursal.id not in self.department.sucursal.ids:
            self.department = ''
        if self.sucursal.id not in self.equipo.sucursal.ids:
            self.equipo = ''
        if self.sucursal.id not in self.tipo_operacion.sucursal.ids:
            self.tipo_operacion = ''
        if self.sucursal.id not in self.negocio.sucursal.ids:
            self.negocio = ''
