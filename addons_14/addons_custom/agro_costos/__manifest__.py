# -*- coding: utf-8 -*-
{
    'name': "Costos",

        'summary': """
        Módulo de Agrovizion para costos
    """,
    'description': """
        Módulo para extender la funcionalidad de costos
    """,
    'author': "Angel Alvarez",
    'website': "http://www.seidor.es",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Costos',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'hr',
        'purchase',
        'account',
        'account_asset',
        'stock',
    ],

    # always loaded
    'data': [
            'security/ir.model.access.csv',
            'views/view_users.xml',
            'views/view_area.xml',
            'views/view_negocio.xml',
            'views/view_departamento.xml',
            'views/view_equipo.xml',
            'views/view_tipo_operacion.xml',
            'views/view_menu.xml',
            'views/view_purchase_order.xml',
            'views/view_account_invoice.xml',
            'views/view_account_payment.xml',
            'views/view_account_move.xml',
            'views/view_account_move_line.xml',
            'views/view_hr_employee.xml',
            'views/view_account_asset.xml',
            'views/account_move_line_auxiliar_view.xml',
            'wizard/view_accounting_assistant.xml',
            'views/view_templates_button.xml',
    ],
    'qweb': [
        'static/src/xml/button.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
