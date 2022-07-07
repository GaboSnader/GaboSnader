{
    'name': "agv_cost_center",

    'summary': """Módulo de Agrovizion para centro de costos""",

    'description': """
        Módulo para extender la funcionalidad de costos
    """,

    'author': "Angel Alvarez",
    'website': "http://www.seidor.es",

    'category': 'Costos',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'sale_stock', 'purchase', 'account_asset'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu_item.xml',
        'views/res_users.xml',
        'views/area.xml',
        'views/equipment.xml',
        'views/type_of_operation.xml',
        'views/business.xml',
        'views/hr_employee.xml',
        'views/purchase_order.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/account_asset.xml',
        'wizard/accounting_assistant.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/button.xml',
    ],

}
