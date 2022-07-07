# -*- encoding: utf-8 -*-
from openerp import release
if release.major_version in ("9.0", "10.0"):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

if release.major_version == "9.0":
    from openerp import api, fields, models, _, tools, release
    from openerp.exceptions import UserError, RedirectWarning, ValidationError
    from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
elif release.major_version in ("10.0","11.0"):
    from odoo import api, fields, models, _, tools, release
    from odoo.exceptions import UserError
    from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

import datetime
from pytz import timezone
import pytz
import tempfile
import base64
import os
import tempfile
import hashlib
from xml.dom import minidom
import time
import codecs
import traceback
import re
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
                
    transport_document_cfdi = fields.Boolean('CFDI Traslado')
    rfcprovcertif = fields.Char('RfcProvCertif', size=64, readonly=True)

    @api.onchange('transport_document_cfdi','type')
    def onchange_transport_dodument(self):
        sat_tipo_obj = self.env['sat.tipo.comprobante']
        if self.transport_document_cfdi:
            if self.transport_document_cfdi == True:
                tipo_id = sat_tipo_obj.search([('code','=','T')], limit=1)
                self.type_document_id = tipo_id[0].id if tipo_id else False
                self.metodo_pago_id = False
                self.pay_method_ids = False
                self.payment_term_id = False
            else:
                if self.type in ('out_invoice','out_refund'):
                    if not self.uso_cfdi_id:
                        raise UserError('Error!\nEl campo Uso CFDI es Obligatorio.')
            
                    if rec.type == 'out_invoice':
                        tipo_id = sat_tipo_obj.search([('code','=','I')], limit=1)
                        self.type_document_id = tipo_id[0].id if tipo_id else False
                    else:
                        tipo_id = sat_tipo_obj.search([('code','=','E')], limit=1)
                        self.type_document_id = tipo_id[0].id if tipo_id else False

    @api.multi
    def action_invoice_open(self):
        sat_tipo_obj = self.env['sat.tipo.comprobante']
        for rec in self:
            if rec.type in ('out_invoice','out_refund'):
                if self.transport_document_cfdi:
                    tipo_id = sat_tipo_obj.search([('code','=','T')], limit=1)
                    self.type_document_id = tipo_id[0].id if tipo_id else False

                if self.transport_document_cfdi == False:
                    if not self.uso_cfdi_id:
                        raise UserError('Error!\nEl campo Uso CFDI es Obligatorio.')
            
                    if rec.type == 'out_invoice':
                        tipo_id = sat_tipo_obj.search([('code','=','I')], limit=1)
                        self.type_document_id = tipo_id[0].id if tipo_id else False
                    else:
                        tipo_id = sat_tipo_obj.search([('code','=','E')], limit=1)
                        self.type_document_id = tipo_id[0].id if tipo_id else False

        res = super(AccountInvoice, self).action_invoice_open()
        attachment_obj = self.env['ir.attachment']
        for rec in self:
            if rec.transport_document_cfdi:
                fname_invoice = rec.fname_invoice
                attachment_xml_ids = attachment_obj.search([('res_model','=','account.invoice'),('res_id','=',rec.id),('name','like','.xml')])
                if attachment_xml_ids:
                    attach_browse = attachment_xml_ids[0]
                    cfd_data = base64.decodestring(attach_browse.datas)
                    cfdi_minidom = minidom.parseString(cfd_data)
                    subnode = cfdi_minidom.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
                    rfcprovcertif = subnode.getAttribute('RfcProvCertif') if subnode.getAttribute('RfcProvCertif') else ''
                    rec.write({'rfcprovcertif':rfcprovcertif})
        return res

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        sat_tipo_obj = self.env['sat.tipo.comprobante']
        type_document = res.type
        if res.transport_document_cfdi:
            tipo_id = sat_tipo_obj.search([('code','=','T')], limit=1)
            res.type_document_id = tipo_id[0].id if tipo_id else False
            return res
        if type_document == 'out_invoice':
            tipo_id = sat_tipo_obj.search([('code','=','I')], limit=1)
            res.type_document_id = tipo_id[0].id if tipo_id else False
        elif type_document == 'out_refund':
            tipo_id = sat_tipo_obj.search([('code','=','E')], limit=1)
            res.type_document_id = tipo_id[0].id if tipo_id else False
        return res



    @api.constrains('transport_document_cfdi','metodo_pago_id','pay_method_ids')
    def _constraint_transport_document(self):
        if self.transport_document_cfdi:
            if self.metodo_pago_id:
                raise UserError(_("La Factura de traslado no requiere Metodo de Pago."))
            if self.pay_method_ids:
                raise UserError(_("La Factura de traslado no requiere Forma de Pago."))
            if self.tax_line_ids:
                raise UserError(_("La Factura de traslado no requiere Impuestos."))
            if self.amount_total != 0.0:
                raise UserError(_("La Factura de traslado no requiere especificar Montos, debe ser igual 0.0."))
        return True

    @api.multi
    def _get_facturae_invoice_dict_data(self):
        res = super(AccountInvoice, self)._get_facturae_invoice_dict_data()
        if self.transport_document_cfdi:
            #### Pensado para CFDI Traslado ######
            if type(res[0]) == list:
                res[0][0]['cfdi:Comprobante'].pop('cfdi:Impuestos')
                res[0][0]['cfdi:Comprobante'].pop('MetodoPago')
                res[0][0]['cfdi:Comprobante'].pop('FormaPago')
                if 'CondicionesDePago' in res[0][0]['cfdi:Comprobante']:
                    res[0][0]['cfdi:Comprobante'].pop('CondicionesDePago')
                res[0][0]['cfdi:Comprobante'].update({'TipoDeComprobante':'T'})
                for concepto in res[0][0]['cfdi:Comprobante']['cfdi:Conceptos']:
                    concepto['cfdi:Concepto'].pop('cfdi:Impuestos')

            else:
                res[0]['cfdi:Comprobante'].pop('cfdi:Impuestos')
                res[0]['cfdi:Comprobante'].pop('MetodoPago')
                res[0]['cfdi:Comprobante'].pop('FormaPago')
                if 'CondicionesDePago' in res[0]['cfdi:Comprobante']:
                    res[0]['cfdi:Comprobante'].pop('CondicionesDePago')
                res[0]['cfdi:Comprobante'].update({'TipoDeComprobante':'T'})
                for concepto in res[0]['cfdi:Comprobante']['cfdi:Conceptos']:
                    concepto['cfdi:Concepto'].pop('cfdi:Impuestos')
            sat_tipo_obj = self.env['sat.tipo.comprobante']
            tipo_id = sat_tipo_obj.search([('code','=','T')], limit=1)
            self.write({'type_document_id': tipo_id[0].id if tipo_id else False})
        return res