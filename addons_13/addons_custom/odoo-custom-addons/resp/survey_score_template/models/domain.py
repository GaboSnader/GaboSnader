# -*- coding:utf-8 -*-
from odoo import models, fields, api

class Domain(models.Model):
    _name = 'survey_score_template.domain'

    name = fields.Char(string='Nombre')
    category_id = fields.Many2one('survey_score_template.category',string=u"Categoría")
    dimension_id = fields.One2many('survey_score_template.dimension', 'domain_id', 'Dimensión')
    null = fields.Float(string='Nulo o despreciable')
    low = fields.Float(string='Bajo')
    medium = fields.Float(string='Medio')
    high = fields.Float(string='Alto')
    very_high = fields.Float(string='Muy alto')
    survey_id = fields.Many2one('survey.survey',string='Encuesta')