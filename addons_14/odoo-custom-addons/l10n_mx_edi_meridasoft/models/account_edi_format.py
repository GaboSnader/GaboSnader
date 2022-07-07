# -*- coding: utf-8 -*-
import datetime
import pytz
import base64
import logging
import xml.dom.minidom

from lxml import etree
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError, Warning
from suds.client import Client

_logger = logging.getLogger(__name__)

class AccountEdiFormatMS(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_get_ms_pac_credentials(self, move):
        if move.company_id.l10n_mx_edi_pac_test_env:
            return {
                'username': 'administrador@meridasoft.com',
                'password': '7c4a8d09ca3762af61e59520943dc26494f8941b',
                'sign_url': 'https://facturacion.demo-pruebas.com/servidor_nusoap?wsdl',
                'cuenta': 'EKU9003173C9',
                'cancel_url': 'https://facturacion.demo-pruebas.com/servidor_nusoap?wsdl',
            }
        else:
            if not move.company_id.l10n_mx_edi_pac_username or not move.company_id.l10n_mx_edi_pac_password:
                return {
                    'errors': [_("The username and/or password are missing.")]
                }

            return {
                'username': move.company_id.l10n_mx_edi_pac_username,
                'password': move.company_id.l10n_mx_edi_pac_password,
                'sign_url': 'https://factura.meridasoft.com/public/servidor_nusoap?wsdl',
                'cancel_url': 'https://factura.meridasoft.com/public/servidor_nusoap?wsdl',
            }

    def _l10n_mx_edi_ms_pac_sign(self, move, credentials, cfdi):
        try:
            client = Client(credentials['sign_url'])
            response = client.service.Facturar_xml_sin_sello(cfdi, credentials['username'], credentials['password'])
            _logger.error("****"+str(cfdi))
        except Exception as e:
            return {
                'errors': [_("The Méridasoft service failed to sign with the following error: %s", str(e))],
            }

        if response.msgError:
            msg = response.msgError
            errors = []
            if msg:
                errors.append(_("Message : %s") % msg)
            return {'errors': errors}

        cfdi_signed = getattr(response, 'xml', None)
        if cfdi_signed:
            cfdi_signed = cfdi_signed.encode('utf-8')

        return {
            'cfdi_signed': cfdi_signed,
            'cfdi_encoding': 'str',
        }

    def _l10n_mx_edi_ms_pac_cancel(self, move, credentials, cfdi):
        uuid = move.l10n_mx_edi_cfdi_uuid
        certificates = move.company_id.l10n_mx_edi_certificate_ids
        certificate = certificates.sudo().get_valid_certificate()
        company = move.company_id
        cer_pem = certificate.get_pem_cer(certificate.content)
        key_pem = certificate.get_pem_key(certificate.key, certificate.password)
        try:
            client = Client(credentials['cancel_url'])
            uuid_type = client.get_type('ns0:stringArray')()
            uuid_type.string = [uuid]
            invoices_list = client.get_type('ns1:UUIDS')(uuid_type)
            response = client.service.cancelar(
                invoices_list,
                credentials['username'],
                credentials['password'],
                company.vat,
                cer_pem,
                key_pem,
            )
        except Exception as e:
            return {
                'errors': [_("The Méridasoft service failed to cancel with the following error: %s", str(e))],
            }

        if not getattr(response, 'Folios', None):
            code = getattr(response, 'CodEstatus', None)
            msg = _("Cancelling got an error") if code else _('A delay of 2 hours has to be respected before to cancel')
        else:
            code = getattr(response.Folios.Folio[0], 'EstatusUUID', None)
            cancelled = code in ('201', '202')  # cancelled or previously cancelled
            # no show code and response message if cancel was success
            code = '' if cancelled else code
            msg = '' if cancelled else _("Cancelling got an error")

        errors = []
        if code:
            errors.append(_("Code : %s") % code)
        if msg:
            errors.append(_("Message : %s") % msg)
        if errors:
            return {'errors': errors}

        return {'success': True}

    def _l10n_mx_edi_ms_pac_sign_invoice(self, invoice, credentials, cfdi):
        return self._l10n_mx_edi_ms_pac_sign(invoice, credentials, cfdi)

    def _l10n_mx_edi_ms_pac_cancel_invoice(self, invoice, credentials, cfdi):
        return self._l10n_mx_edi_ms_pac_cancel(invoice, credentials, cfdi)

    def _l10n_mx_edi_ms_pac_sign_payment(self, move, credentials, cfdi):
        return self._l10n_mx_edi_ms_pac_sign(move, credentials, cfdi)

    def _l10n_mx_edi_ms_pac_cancel_payment(self, move, credentials, cfdi):
        return self._l10n_mx_edi_ms_pac_cancel(move, credentials, cfdi)
