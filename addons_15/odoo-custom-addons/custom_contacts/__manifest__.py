# -*- coding: utf-8 -*-
{
    'name': 'custom_contacts',
    'version': '15.0',
    'description': 'Añade funcionalidades de contactos y contratos',
    'author': 'Meridasoft',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'base',
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/documentos_expediente_view.xml',
        'wizard/get_contract_view.xml',
        'reports/paperformat.xml',
        'reports/promesa_compraventa.xml',
        'reports/rescision_contrato.xml',
        'reports/solicitud_rescision.xml',
        'reports/traslativo_dominio.xml',
        'reports/socio_constructor.xml',
    ],
    # 'images': ['static/src/img/icon.png'],
    # only loaded in demonstration mode
    'demo': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}
