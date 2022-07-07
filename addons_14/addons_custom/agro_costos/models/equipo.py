# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
#clase ligada al equipo de mantenimiento maintenance.equipment ver equipment.py
class Equipo(models.Model):
    _name = 'costos.equipo'
    _inherit = 'mail.thread'
    _rec_name = 'equipo'
    _description = "Equipo"

    clave = fields.Char(string='Clave', required=True, index=True)
    equipo = fields.Char(string='Equipo', required=False)
    active = fields.Boolean (string="Estatus", required=False, default = True)
    _sql_constraints = [
        ('equipo_clave_uniq',
        'check (1=1)',
        'La clave del equipo debe ser unica!')]
    sucursal = fields.Many2many('stock.warehouse', required=True, string='Sucursal')
    company_id = fields.Many2one('res.company',string='Empresa', default=lambda self: self._default_company())
    description = fields.Text(string='Descripción')

    
    def _default_branch(self):
        context = self._context
        _uid = self.env.user.id
        branch_default = self.env['hr.employee'].search([('user_id','=',_uid)])
        return branch_default.branches.id

    
    def _default_company(self):
        context = self._context
        _uid = self.env.user.id
        company_default = self.env['hr.employee'].search([('user_id','=',_uid)])
        return company_default.company_id.id

    
    def write(self,vals):
        #no se debe permitir la modificación del registro con clave GEN ya que es el generico por default
        #en self.clave tenemos el valor anterior
        #en vals.get('clave') tenemos el valor actualizado
        #cualquier modificacion en mantenimiento se refleja en costos
        if str(self.clave) == 'GEN':
            _logger.error("valores---->>>>> " + str(vals.get('clave')) )
            if vals.get('clave')  is not None: #intentan cambiar la clave?
                if vals.get('clave') != 'GEN':
                    raise ValidationError('No se debe modificar la clave  General.')
            if vals.get('equipo') is not None: 
                 if vals.get('equipo') != 'General':
                     raise ValidationError('No se debe modificar el equipo  General.')
            if vals.get('active') is not None: 
                if vals.get('active') != 1:
                    raise ValidationError('No se debe desactivar el equipo   General.')
            # if vals.get('description') is not None:
            #     if vals.get('description') != 'General':
            #         raise ValidationError('No se debe modificar la descripción del equipo de   General.')
        res = super(Equipo, self).write(vals)# todos los valores de vals a res
        return res
    #si eliminan el equipo en mantenimiento se elimina tambien en costos
    
    def unlink(self):
        if str(self.clave) == 'GEN':
             raise ValidationError('No se debe eliminar la clave  General.')
        return super(Equipo, self).unlink()



