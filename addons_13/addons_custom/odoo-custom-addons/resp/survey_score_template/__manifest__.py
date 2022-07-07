#-*- coding: utf-8 -*-
{
    'name': "Template score",
    'summary': """
        Template score
    """,
    'description': """
        Template for score survey
    """,
    'author': "Daniel Chuc",
    'category': '',
    'version': '0.2',
    'depends': [
        'base',
        'survey',
        'survey_take_photo',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/survey_survey.xml',
        'views/survey_question.xml',
        'views/category.xml',
        'views/domain.xml',
        'views/dimension.xml',
        'views/qualification.xml',
        'views/continuity.xml',
        'views/survey_traumatic.xml',
        'views/survey_employee.xml',
        'template/survey_nom.xml',
        'template/survey_terms.xml',
        'template/survey_date.xml',
        'template/survey_employee.xml',
        'template/survey_score.xml',
        'template/survey_templates.xml',
        'template/survey_traumatic.xml',
        'template/survey_thanks.xml',
        'template/survey_error.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}