# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    #campos costos
    sucursal = fields.Many2one('stock.warehouse',string='Sucursal')
    department = fields.Many2one('costos.departamento',string='Departamento')
    area = fields.Many2one('costos.area',string='Area')
    equipo = fields.Many2one('costos.equipo',string='Equipo')
    tipo_operacion = fields.Many2one('costos.tipo_operacion',string='Tipo de Operación')
    negocio = fields.Many2one('costos.negocio',string='Negocio')

    #nos devuelve la vista cargando la informacion del res.users
    def searchcostosusers(self):
        return {
            'name': _('Costos'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.users',
            'view_id':self.env['ir.ui.view'].search([('name', '=', 'costos.users.form')],limit=1).id,
            'res_id':self.id,
            'type': 'ir.actions.act_window'
            }
    
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
    #Actualiza el filtro de negocio con las opciones validas para la sucursal seleccionada
    @api.onchange('sucursal','negocio')
    def _fill_area(self):
        l_suc = []
        for suc in self.sucursal:
            l_suc.append(int(suc[0]))
        return {'domain':{'negocio': [('sucursal', 'in', l_suc)]}}  
    #Actualiza el filtro de equipo con las opciones validas para la sucursal seleccionada
    @api.onchange('sucursal','equipo')
    def _fill_equipo(self):
        l_suc = []
        for suc in self.sucursal:
            l_suc.append(int(suc[0]))
        return {'domain':{'equipo': [('sucursal', 'in', l_suc)]}} 
    #Actualiza el filtro de tipo de operacion con las opciones validas para la sucursal seleccionada
    @api.onchange('sucursal','tipo_operacion')
    def _fill_tipo_operacion(self):
        l_suc = []
        for suc in self.sucursal:
            l_suc.append(int(suc[0]))
        return {'domain':{'tipo_operacion': [('sucursal', 'in', l_suc)]}} 
    
    #si se cambia la sucursal se limpian los campos
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


