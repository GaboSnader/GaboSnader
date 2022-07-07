# -*- coding:utf-8 -*-
from odoo import models, fields, api

class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    require_photo = fields.Boolean(string='¿Requiere foto?')