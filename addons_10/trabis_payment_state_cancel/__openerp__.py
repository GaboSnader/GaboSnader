# -*- coding: utf-8 -*-

{
    'name': 'Estado cancelado en pagos',
    'version': '1',
    'category': 'Trabis',
    'description': """
    Modulo que crea el estado 'cancelado' para pagos
    El boton cancelar ahora pasa el estado del pago a 'cancelado'
    Se crea un boton que regresa el pago a estado borrador cuando esta cancelado
    """,
    'author': 'Marco Cid',
    'website': 'http://www.trabis.com.mx',
    'depends': ["account_cancel"],
    'data': [
        'account_payment_view.xml',
    ],
    # 'qweb': [ 
    #     "static/src/base.xml", 
    # ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
