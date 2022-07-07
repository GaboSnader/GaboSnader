# -*- coding:utf-8 -*-
from odoo import models, fields, api

class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    qualification_id = fields.Many2one('survey_score_template.qualification',string=u'Calificación')
    sequence = fields.Integer('Secuencia')
    date_start = fields.Date(string='Fecha de inicio')