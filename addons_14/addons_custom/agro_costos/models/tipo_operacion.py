# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TipoOperacion(models.Model):
    _name = 'costos.tipo_operacion'
    _inherit = 'mail.thread'
    _rec_name = 'tipo_operacion'
    _description = "Tipo de Operación"

    clave = fields.Char(string='Clave', required=True,index=True, track_visibility=True)
    tipo_operacion = fields.Char(string='Tipo de Operación',required=False,track_visibility=True)
    active = fields.Boolean (string="Estatus", required=False, default = True)
    _sql_constraints = [
        ('equipo_clave_uniq',
        'UNIQUE (clave)',
        'La clave del Tipo de Operación debe ser unica!')]
    sucursal = fields.Many2many('stock.warehouse',string='Sucursal',track_visibility='onchange',required=True)
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
    
    def write(self,vals):
        #no se debe permitir la modificación del registro con clave GEN ya que es el generico por default
        #en self.clave tenemos el valor anterior
        #en vals.get('clave') tenemos el valor actualizado
        if str(self.clave) == 'GEN':
            
            if vals.get('clave')  is not None: #intentan cambiar la clave?
              if vals.get('clave') != 'GEN':
                raise ValidationError('No se debe modificar la clave  General.')
            if vals.get('tipo_operacion') is not None: 
               if vals.get('tipo_operacion') != 'General':
                raise ValidationError('No se debe modificar el Tipo de Operación General.')
            if vals.get('active') is not None: 
              if vals.get('active') != 1:
                raise ValidationError('No se debe desactivar el Tipo de Operación General.')
            if vals.get('description') is not None:
              if vals.get('description') != 'General':
                raise ValidationError('No se debe modificar la descripción del Tipo de Operación General.')
        res = super(TipoOperacion, self).write(vals)# todos los valores de vals a res
        return res

    
    def unlink(self):
        for rec in self:
            if str(rec.clave) == 'GEN':
                raise ValidationError('No se debe eliminar el Tipo de Operación General.')
        return super(TipoOperacion, self).unlink()


    
    def _default_company(self):
        context = self._context
        _uid = self.env.user.id
        company_default = self.env['hr.employee'].search([('user_id','=',_uid)])
        return company_default.company_id.id