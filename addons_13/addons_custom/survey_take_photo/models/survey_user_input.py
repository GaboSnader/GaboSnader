# -*- coding:utf-8 -*-
from odoo import models, fields, api

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    picture = fields.Binary(string='Imagen')