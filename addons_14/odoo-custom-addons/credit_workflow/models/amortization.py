# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

class Amortization(models.Model):
    _name = 'credit_workflow.amortization'

    name = fields.Char(string="Nombre")
    month = fields.Char(string="mes")
    total = fields.Float(string="mes")
    credit_request_id = fields.Many2one(
        'credit_workflow.credit_request',
        string="Solicitud de credito"
    )