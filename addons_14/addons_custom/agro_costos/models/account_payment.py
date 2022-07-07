# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class AccountPayment(models.Model):
    _name =    'account.payment'
    _inherit = 'account.payment'

    sucursal = fields.Many2one('stock.warehouse',string='Sucursal',default=lambda self:self.env.user.sucursal.id)
    equipo = fields.Many2one('costos.equipo',string='Equipo',default=lambda self:self.env.user.equipo.id)
    negocio  = fields.Many2one('costos.negocio',string='Negocio',default=lambda self:self.env.user.negocio.id)
    area  = fields.Many2one('costos.area',string='Area',default=lambda self:self.env.user.area.id)
    department = fields.Many2one('costos.departamento',string='Departamento',default=lambda self:self.env.user.department.id)
    tipo_operacion = fields.Many2one('costos.tipo_operacion',string='Tipo de Operación',default=lambda self:self.env.user.tipo_operacion.id)
    costos_heredados = fields.Boolean('Costos heredados')


    @api.model
    def default_get(self, fields_list):
        res = super(AccountPayment, self).default_get(fields_list)
        if 'default_invoice_ids' in self.env.context.keys():
            invoice = self.env['account.move'].browse(self.env.context['default_invoice_line_ids'][0][1])
            res.update({
                'sucursal':invoice.sucursal.id if invoice.sucursal else False,
                'equipo':invoice.equipo.id if invoice.equipo else False,
                'negocio':invoice.negocio.id if invoice.negocio else False,
                'area':invoice.area.id if invoice.area else False,
                'department':invoice.department.id if invoice.department else False,
                'tipo_operacion':invoice.tipo_operacion.id if invoice.tipo_operacion else False,
                'costos_heredados' : True
            })
        return res
    
    # Este metodo se invoca cuando se crea el asiento contable del pago, es decir, la informacion de cabecera de la poliza
    def _get_move_vals(self, journal=None):
        move_vals = super(AccountPayment, self)._get_move_vals(journal)
        move_vals.update({
            'sucursal' : self.sucursal.id if self.sucursal else False,
            'equipo' : self.equipo.id if self.equipo else False,
            'negocio' : self.negocio.id if self.negocio else False,
            'area' : self.area.id if self.area else False,
            'department' : self.department.id if self.department else False,
            'tipo_operacion' : self.tipo_operacion.id if self.tipo_operacion else False,
        })
        return move_vals
    
    # Este metodo se invoca cuando se crean los apuntes contables que no son liquidez, es decir, las lineas que afectan las cuentas de los clientes
    def _get_counterpart_move_line_vals(self, invoice=False):
        move_vals = super(AccountPayment, self)._get_counterpart_move_line_vals(invoice)
        move_vals.update({
            'sucursal' : self.sucursal.id if self.sucursal else False,
            'equipo' : self.equipo.id if self.equipo else False,
            'negocio' : self.negocio.id if self.negocio else False,
            'area' : self.area.id if self.area else False,
            'department' : self.department.id if self.department else False,
            'tipo_operacion' : self.tipo_operacion.id if self.tipo_operacion else False,
        })
        return move_vals
        
    # Este metodo se invoca cuando se crea el apunte contable de liquidez, es decir, la linea que representa el movimiento que afecta la cuenta de banco
    def _get_liquidity_move_line_vals(self, amount):
        move_vals = super(AccountPayment, self)._get_liquidity_move_line_vals(amount)
        move_vals.update({
            'sucursal' : self.sucursal.id if self.sucursal else False,
            'equipo' : self.equipo.id if self.equipo else False,
            'negocio' : self.negocio.id if self.negocio else False,
            'area' : self.area.id if self.area else False,
            'department' : self.department.id if self.department else False,
            'tipo_operacion' : self.tipo_operacion.id if self.tipo_operacion else False,
        })
        return move_vals


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