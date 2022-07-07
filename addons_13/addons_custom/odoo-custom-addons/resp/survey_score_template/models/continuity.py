# -*- coding:utf-8 -*-
from odoo import models, fields, api

class Continuity(models.Model):
    _name = 'survey_score_template.continuity'

    name = fields.Char(string='Nombre')
    surveys_ids = fields.Many2many(
        'survey.survey',
        string='Secuencia'
    )