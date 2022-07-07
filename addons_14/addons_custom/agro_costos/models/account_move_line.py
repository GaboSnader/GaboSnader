
# -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    sucursal = fields.Many2one('stock.warehouse',string='Sucursal' )
    equipo = fields.Many2one('costos.equipo',string='Equipo' )
    negocio  = fields.Many2one('costos.negocio',string='Negocio')
    area  = fields.Many2one('costos.area',string='Area')
    department = fields.Many2one('costos.departamento',string='Departamento')
    tipo_operacion = fields.Many2one('costos.tipo_operacion',string='Tipo de Operación')
    saldo_inicial = fields.Monetary(string='Saldo inicial')
    saldo_final = fields.Monetary(string='Saldo final')
    