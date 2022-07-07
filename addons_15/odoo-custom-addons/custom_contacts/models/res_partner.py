# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    birthday_date = fields.Date(string="Fecha de Nacimiento", required=True)
    birthday_country = fields.Many2one('res.country', string="País de Nacimiento", required=True)
    job_occupation = fields.Char(string="Ocupación de trabajo", required=True)
    curp = fields.Char(string="CURP", size=18)
    document_id = fields.Char(string="Documento de Identificación")
    document_response = fields.Char(string="Autoridad que emite")
    document_number = fields.Char(string="Número (Folio) de la identificación")


