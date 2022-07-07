# -*- coding:utf-8 -*-
from odoo import models, fields, api

class Qualification(models.Model):
    _name = 'survey_score_template.qualification'

    name = fields.Char(string='Nombre')
    nullo = fields.Float(string='Nulo o despreciable')
    low = fields.Float(string='Bajo')
    medium = fields.Float(string='Medio')
    high = fields.Float(string='Alto')
    very_high = fields.Float(string='Muy alto')