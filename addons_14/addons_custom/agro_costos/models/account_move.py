# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    sucursal = fields.Many2one('stock.warehouse',string='Sucursal',default=lambda self:self.env.user.sucursal.id)
    equipo = fields.Many2one('costos.equipo',string='Equipo',default=lambda self:self.env.user.equipo.id)
    negocio  = fields.Many2one('costos.negocio',string='Negocio',default=lambda self:self.env.user.negocio.id)
    area  = fields.Many2one('costos.area',string='Area',default=lambda self:self.env.user.area.id)
    department = fields.Many2one('costos.departamento',string='Departamento',default=lambda self:self.env.user.department.id)
    tipo_operacion = fields.Many2one('costos.tipo_operacion',string='Tipo de Operación',default=lambda self:self.env.user.tipo_operacion.id)

    
    @api.onchange('sucursal','department')
    def _fill_department(self):
        l_suc = []
        for suc in self.sucursal:
            l_suc.append(int(suc[0]))
        return {'domain':{'department': [('sucursal', 'in', l_suc)]}} 
    #Actualiza el filtro de area con las opciones validas para la sucursal seleccionada
    @api.onchange('sucursal','area')
    def _fill_area(self):
        l_suc = []
        for suc in self.sucursal:
            l_suc.append(int(suc[0]))
        return {'domain':{'area': [('sucursal', 'in', l_suc)]}} 

    @api.onchange('sucursal','equipo')
    def _fill_equipo(self):
        l_suc = []
        for suc in self.sucursal:
            l_suc.append(int(suc[0]))
        return {'domain': {'equipo': [('sucursal', 'in', l_suc)]}}

    @api.onchange('sucursal','negocio')
    def _fill_negocio(self):
        l_suc = []
        for suc in self.sucursal:
            l_suc.append(int(suc[0]))
        return {'domain': {'negocio': [('sucursal', 'in', l_suc)]}}

    @api.onchange('sucursal','tipo_operacion')
    def _fill_tipo_operacion(self):
        l_suc = []
        for suc in self.sucursal:
            l_suc.append(int(suc[0]))
        return {'domain': {'tipo_operacion': [('sucursal', 'in', l_suc)]}} 
    
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

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        if self.move_type == 'in_invoice':
            self.invoice_line_ids.sucursal = self.sucursal.id
            self.invoice_line_ids.area = self.area.id
            self.invoice_line_ids.equipo = self.equipo.id
            self.invoice_line_ids.department = self.department.id
            self.invoice_line_ids.negocio = self.negocio.id
            self.invoice_line_ids.tipo_operacion = self.tipo_operacion.id
        