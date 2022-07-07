# -*- coding:utf-8 -*-
from odoo import models, fields, api

class Category(models.Model):
    _name = 'survey_score_template.category'

    name = fields.Char(string='Nombre')
    domain_id = fields.One2many('survey_score_template.domain', 'category_id', 'Dominio')
    nullo = fields.Float(string='Nulo o despreciable')
    low = fields.Float(string='Bajo')
    medium = fields.Float(string='Medio')
    high = fields.Float(string='Alto')
    very_high = fields.Float(string='Muy alto')
    survey_id = fields.Many2one('survey.survey',string='Encuesta')