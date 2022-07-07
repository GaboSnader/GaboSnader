# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sucursal = fields.Many2one('stock.warehouse',string='Sucursal', store=True)
    equipo = fields.Many2one('costos.equipo',string='Equipo', store=True)
    negocio  = fields.Many2one('costos.negocio',string='Negocio', store=True)
    area  = fields.Many2one('costos.area',string='Area', store=True)
    department = fields.Many2one('costos.departamento',string='Departamento', store=True)
    tipo_operacion = fields.Many2one('costos.tipo_operacion',string='Tipo de Operación', store=True)    
 
    @api.onchange('sucursal','department')
    def _fill_department(self):
        l_suc = []
        for suc in self.sucursal:
           l_suc.append(int(suc[0]))
        return {'domain': {'department': [('sucursal', 'in', l_suc)]}} 

    @api.onchange('sucursal','area')
    def _fill_area(self):
        l_suc = []
        for suc in self.sucursal:
            l_suc.append(int(suc[0]))
        return {'domain': {'area': [('sucursal', 'in', l_suc)]}}
    
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

    @api.onchange('product_id')
    def auto_costos(self):
        self.update({ 
            'sucursal': self.order_id.sucursal.id,
            'equipo': self.order_id.equipo.id,
            'negocio': self.order_id.negocio.id,
            'area': self.order_id.area.id,
            'department': self.order_id.department.id,
            'tipo_operacion': self.order_id.tipo_operacion.id,
            })

    @api.onchange('sucursal')
    def _blank_fields(self):
        if self.product_id.id:
            self.area = ''
            self.department = ''
            self.equipo = ''
            self.tipo_operacion = ''
            self.negocio = ''
              