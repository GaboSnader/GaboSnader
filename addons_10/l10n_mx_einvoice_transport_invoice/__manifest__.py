# -*- coding: utf-8 -*-

{
    "name": "Comprobante Electronico para Traslados",
    "version": "1.0",
    "author": "Argil Consulting SA de CV & German Ponce Dominguez",
    "category": "Localization/Mexico",
    "description": """

Comprobante Traslado
====================

Este modulo permite incorporar el CFDI de Traslado para la Facturación Electronica 3.3

""",
    "website": "http://www.argil.mx",
    "license": "AGPL-3",
    "depends": [
        "l10n_mx_einvoice",
        "l10n_mx_einvoice_payment",
        "l10n_mx_sat_models",
        "l10n_mx_sat_models_datas",
        "l10n_mx_einvoice_report",
        ],
    "data"    : [
                 'account_invoice_view.xml',
                 'invoice_facturae_10.xml',
    ],
    "installable": True,
}
