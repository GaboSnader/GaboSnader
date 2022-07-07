# -*- coding: utf-8 -*-
{
    'name': "Club Deportivo ALI",
    'summary': """
        Módulo para club deportivo ALI
        """,
    'description': """
        Módulo para extender la funcionalidades de odoo para el club deportivo de ALI
    """,
    'author': "MeridaSoft",
    'website': "http://www.meridasoft.com",
    'category': 'suscriptions',
    'version': '15.0',
    'depends': ['base'],
    'data': [
        'data/res_partner_sequence.xml',
        'views/res_partner_view.xml',
    ],
    #HOLA AQUI ESTOY!!!
    'installable': True,
    'auto_install': False,
    'application': True,
}
