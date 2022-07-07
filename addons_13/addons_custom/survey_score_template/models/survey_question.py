# -*- coding:utf-8 -*-
from odoo import models, fields, api

class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    optional = fields.Boolean(string='Respuesta opcional')