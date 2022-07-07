# # -*- coding:utf-8 -*-
import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)

class SurveyLabel(models.Model):
    _inherit = 'survey.label'

    category_id = fields.Many2one('survey_score_template.category',string="Categoría",domain=lambda self: self._get_domain())
    domain_id = fields.Many2one('survey_score_template.domain',string="Dominio")
    dimension_id = fields.Many2one('survey_score_template.dimension',string="Dimensión")

    @api.onchange('category_id')
    def change_category(self):
        self.domain_id = False
        self.dimension_id = False
        return {'domain':{'domain_id': [('category_id', '=',self.category_id.id)]}}

    @api.onchange('domain_id')
    def change_domain(self):
        self.dimension_id = False
        return {'domain':{'dimension_id': [('domain_id', '=',self.domain_id.id)]}}

    def _get_domain(self):
        domain = False
        survey = self.env.context.get('default_survey_id')
        category = self.env['survey_score_template.category'].search([('survey_id','=',survey)])
        if category:
            domain = "[('id', 'in', %s)]" % category.ids
        return domain