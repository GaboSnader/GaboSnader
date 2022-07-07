# -*- coding: utf-8 -*-
{
    'name': "base module for Geo, Locate and Draw into map for odoo addons",

    'summary': "base module for showing entities in open street map, draw and geocoding",
    'description': """
        base module for showing entities in open street map, draw and geocoding,
    """,
    "category": "Web",
    'author': "0Solver0",
    'version': '13.0',
    'website': 'https://addons4.odoo.com/',
    'license': 'LGPL-3',
    # 'price': '100',
    # 'currency': 'USD',
    'depends': ['web'],
    'data': [
         "views/assets.xml",
         "views/data.xml",
         "data/data_data.xml",
         'security/ir.model.access.csv',
    ],
    'images': ['static/description/thumbnails_screenshot.png','static/description/icon.png'],
    'qweb': ['static/src/xml/solmaptemplate.xml','static/src/xml/solmapform.xml'],
    'installable': True,
    'uninstall_hook': 'uninstall_hook',
    'auto_install': False
}
