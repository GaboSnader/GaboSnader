#-*- coding: utf-8 -*-
{
    'name': "Take a photo",
    'summary': """
        Take a photo
    """,
    'description': """
        Take a photo when survey start
    """,
    'author': "Daniel Chuc",
    'category': '',
    'version': '0.2',
    'depends': [
        'base',
        'survey',
        'website'
    ],
    'data': [
        'views/survey_views.xml',
        'views/survey_templates.xml',
        'views/survey_user_input_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

