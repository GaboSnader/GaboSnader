# -*- coding: utf-8 -*-

# Copyright © 2018-2020 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

{
    'name': 'Website Facebook Pixel',
    'version': '14.0.1.0.1',
    'category': 'Website',
    'author': 'Garazd Creation',
    'website': 'https://garazd.biz',
    'license': 'LGPL-3',
    'summary': 'Add the Facebook Pixel event PageView to all website pages.',
    'images': ['static/description/banner.png'],
    'live_test_url': 'https://garazd.biz/r/Vw7',
    'description': """
Track Website Activities, Improve Your Return on Advertising, Reach New and Existing Customers
    """,
    'depends': [
        'website',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/website_templates.xml',
    ],
    'external_dependencies': {
    },
    'support': 'support@garazd.biz',
    'application': False,
    'installable': True,
    'auto_install': False,
}
