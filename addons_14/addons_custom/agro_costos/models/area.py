# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Area(models.Model):
    
    _name = 'costos.area'
    _inherit = 'mail.thread'
    _rec_name = 'area'
    _description = "Área"
 
    clave = fields.Char(string='Clave',store=True, track_visibility=True)
    area = fields.Char(string='Área',store=True, track_visibility=True)
    active = fields.Boolean (string="Estatus", required=False, default=True)
    _sql_constraints = [
        ('equipo_clave_uniq',
        'CHECK(1=1)',
        'La clave del Area debe ser unica!')]
    sucursal = fields.Many2many('stock.warehouse',string='Sucursal',track_visibility=True,required=True)
    company_id = fields.Many2one('res.company', string='Empresa',default=lambda self: self._default_company(),track_visibility=True)
    description = fields.Text(string='Descripción',track_visibility=True)
    department_id = fields.Many2one('hr.department',string="Nombre de departamento",required=True,track_visibility=True)
    list_sucursal = fields.Text(string='sucursal',track_visibility=True)


    @api.onchange('sucursal')
    def _onchange(self):
        acumulador = ""
        for x in self.sucursal:
            obj = x.name + " - "
            acumulador += obj
        self.list_sucursal = acumulador
    
    
    @api.depends('department_id')
    def _compute_clave_area(self):
        if self.department_id:
            self.clave = str(self.department_id.name).upper()
            self.area = str(self.department_id.name).upper()
            
    
    def _default_company(self):
        context = self._context
        _uid = self.env.user.id
        company_default = self.env['hr.employee'].search([('user_id','=',_uid)])
        return company_default.company_id.id