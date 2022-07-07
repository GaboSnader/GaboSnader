# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

class RequestCredit(models.Model):
    _name = 'credit_workflow.credit_request'

    name = fields.Char(string="Nombre")
    partner_id = fields.Many2one('res.partner', string="Cliente")
    state = fields.Selection([
        ('draft','Borrador'),
        ('sent', 'Solicitud Enviada'),
        ('approve','Aprobado'),
        ('refuse','Rechazado'),
        ('cancel','Cancelado'),
        ], string="Estado", default="draft")
    term = fields.Integer(string="plazo")
    months = fields.Selection([
        ('3','3'),
        ('6','6'),
        ('9','9'),
        ('12','12'),
        ('18','18'),
        ('24','24'),
        ('36','36'),
        ('60','60'),
        ('72','72'),])
    
    amortization = fields.One2many(
        'credit_workflow.amortization',
        'credit_request_id', 
        string="Tabla de Amortizacion"
        )
