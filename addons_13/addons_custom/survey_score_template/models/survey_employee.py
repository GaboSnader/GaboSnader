# _*_ coding:utf_8 _*_
from odoo import models, fields, api
from uuid import uuid4

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    workplace_id = fields.Many2one('survey.workplace', string="Centro de trabajo")

class SurveyEmployee(models.Model):
    _name = 'survey_score_template.survey_employee'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users',string='Usuario')
    job_id = fields.Many2one('hr.job',string='Puesto')
    department_id = fields.Many2one('hr.department',string='Departamento')
    sex = fields.Selection(
        selection=[
                ('male', 'Masculino'),
                ('female', 'Femenino'),
                ('other', 'Otro')], string='Sexo')
    year = fields.Char(string='Edad en años')
    level_sf = fields.Char(string='Nivel de estudios (Sin información)')
    level_primary = fields.Char(string='Primaria')
    level_secondary = fields.Char(string='Secundaria')
    level_preparatory = fields.Char(string='Preparatoria o Bachillerato')
    level_technical = fields.Char(string='Técnico Superior')
    level_degree = fields.Char(string='Licenciatura')
    level_mastery = fields.Char(string='Maestria')
    level_doctorate = fields.Char(string='Doctorado')
    job_type = fields.Char(string='Tipo de puesto')
    contract_type = fields.Char(string='Tipo de contratación')
    personal_type = fields.Char(string='Tipo de personal')
    jornal_type = fields.Char(string='Tipo de jornada de trabajo')
    turn = fields.Char(string='Realiza rotación de turno')
    experience_job = fields.Char(string='Tiempo en el puesto actual')
    experience_work = fields.Char(string='Tiempo experiencia laboral')
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