# _*_ coding:utf_8 _*_
from odoo import models, fields, api

class SurveyTraumatic(models.Model):
    _name = 'survey_score_template.survey_traumatic'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users',string='user_id')
    question_1 = fields.Boolean(string='¿Accidente que tenga como consecuencia la muerte, la pérdida de un miembro o una lesión grave?')
    question_2 = fields.Boolean(string='¿Asaltos?')
    question_3 = fields.Boolean(string='¿Actos violentos que derivaron en lesiones graves?')
    question_4 = fields.Boolean(string='¿Secuestro?')
    question_5 = fields.Boolean(string='¿Amenazas?')
    question_6 = fields.Boolean(string='¿Cualquier otro que ponga en riesgo su vida o salud, y/o la de otras personas?')
    question_7 = fields.Boolean(string='¿Ha tenido recuerdos recurrentes sobre el acontecimiento que le provocan malestares?')
    question_8 = fields.Boolean(string='¿Ha tenido sueños de carácter recurrente sobre el acontecimiento, que le producen malestar?')
    question_9 = fields.Boolean(string='¿Se ha esforzado por evitar todo tipo de sentimientos, conversaciones o situaciones que le puedan recordar el acontecimiento?')
    question_10 = fields.Boolean(string='¿Se ha esforzado por evitar todo tipo de actividades, lugares o personas que motivan recuerdos del acontecimiento?')
    question_11 = fields.Boolean(string='¿Ha tenido dificultad para recordar alguna parte importante del evento?')
    question_12 = fields.Boolean(string='¿Ha disminuido su interés en sus actividades cotidianas?')
    question_13 = fields.Boolean(string='¿Se ha sentido usted alejado o distante de los demás?')
    question_14 = fields.Boolean(string='¿Ha notado que tiene dificultad para expresar sus sentimientos?')
    question_15 = fields.Boolean(string='¿Ha tenido la impresión de que su vida se va a acortar, que va a morir antes que otras personas o que tiene un futuro limitado?')
    question_16 = fields.Boolean(string='¿Ha tenido usted dificultades para dormir?')
    question_17 = fields.Boolean(string='¿Ha estado particularmente irritable o le han dado arranques de coraje?')
    question_18 = fields.Boolean(string='¿Ha tenido dificultad para concentrarse?')
    question_19 = fields.Boolean(string='¿Ha estado nervioso o constantemente en alerta?')
    question_20 = fields.Boolean(string='¿Se ha sobresaltado fácilmente por cualquier cosa?')