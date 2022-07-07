# -*- coding:utf-8 -*-
from odoo import models, fields, api

class Dimension(models.Model):
    _name = 'survey_score_template.dimension'

    name = fields.Char(string='Nombre')
    domain_id = fields.Many2one('survey_score_template.domain',string="Dominio")
    null = fields.Float(string='Nulo o despreciable')
    low = fields.Float(string='Bajo')
    medium = fields.Float(string='Medio')
    high = fields.Float(string='Alto')
    very_high = fields.Float(string='Muy alto')
    survey_id = fields.Many2one('survey.survey',string='Encuesta')