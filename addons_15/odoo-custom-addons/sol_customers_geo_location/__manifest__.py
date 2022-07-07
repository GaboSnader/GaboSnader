# -*- coding: utf-8 -*-
{
    'name': "Geo, locate, draw into map case Customer",

    'summary': "Sol map customer. ",
    'description': """
        Sol map test for customer
    """,
    "category": "sale",
    'author': "0Solver0",
    'license': 'LGPL-3',
    'version': '13.0',
    'website': 'https://addons4.odoo.com/',
    'depends': ['sol_ol_map_draw','sale_management','base_geolocalize'],
    'data': [
         "views/data.xml"
    ],
    'images': ['static/description/thumbnails_screenshot.png','static/description/icon.png'],
    'installable': True,
    'auto_install': False
}
