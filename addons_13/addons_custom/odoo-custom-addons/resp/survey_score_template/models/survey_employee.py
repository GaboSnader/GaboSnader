# _*_ coding:utf_8 _*_
from odoo import models, fields, api
from uuid import uuid4

class SurveyEmployee(models.Model):
    _name = 'survey_score_template.survey_employee'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users',string='user_id')
    job_id = fields.Many2one('hr.job',string='job_id')
    department_id = fields.Many2one('hr.department',string='department_id')
    sex = fields.Char(string='sex')
    year = fields.Char(string='year')
    level_sf = fields.Char(string='level_sf')
    level_primary = fields.Char(string='level_primary')
    level_secondary = fields.Char(string='level_secondary')
    level_preparatory = fields.Char(string='level_preparatory')
    level_technical = fields.Char(string='level_technical')
    level_degree = fields.Char(string='level_degree')
    level_mastery = fields.Char(string='level_mastery')
    level_doctorate = fields.Char(string='level_doctorate')
    job_type = fields.Char(string='job_type')
    contract_type = fields.Char(string='contract_type')
    personal_type = fields.Char(string='personal_type')
    jornal_type = fields.Char(string='jornal_type')
    turn = fields.Char(string='turn')
    experience_job = fields.Char(string='experience_job')
    experience_work = fields.Char(string='experience_work')
    token = fields.Char(string='token',default=lambda self: self._get_uuid())
    state = fields.Selection(
        selection=[
                ('draft', 'Borrador'),
                ('terms', 'Terminos'),
                ('employee', 'Datos de empleado'),
                ('traumatic', U'Acontecimientos traumáticos'),
                ('in_surveys', 'En encuestas'),
                ('closed', 'Finalizado'),
        ], default='draft')
    survey = fields.Many2one('survey.survey')
    survey_answer = fields.Integer(string='survey_answer',default=0)
    surveys_to_answer = fields.Integer(string='surveys_to_answer',default=0)
    traumatic = fields.Many2one('survey_score_template.survey_traumatic')

    _sql_constraints = [('unique_id','UNIQUE(user_id)',"Error, el usuario ya existe registrado")]

    def _get_uuid(self):
        return str(uuid4())