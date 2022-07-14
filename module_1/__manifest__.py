# -*- coding: utf-8 -*-
{
    'name': 'Model to El Cepillo',
    'version': '1.0',
    'description': '',
    'author': 'Gabriel Lopez',
    'license': 'LGPL-3',
    'category': 'stock',
    'depends': [
        'stock',
        'sale',
        'product',
        'l10n_mx_edi',
        'sale_enterprise',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_location_view.xml',
        'views/product_template_view.xml',
        'views/sale_report.xml',
        'report/report_account_move.xml',
    ],
    # 'auto_install': True,
    'application': False,
    'installable': True,
} 
