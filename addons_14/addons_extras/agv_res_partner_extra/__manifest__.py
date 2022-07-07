# -*- coding: utf-8 -*-
{
    'name': "agv_res_partner_extra",

    'summary': """Add Customer and Supplier Code""",

    'author': "Edgar Inzunza",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/res_partner.xml',
    ],
}
