# -*- coding:utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round
from datetime import datetime
import base64
import xmltodict
import logging


_logger = logging.getLogger(__name__)


class HrExpenseReadXml(models.TransientModel):

    _name = 'hr_expense_v15.hr_expense_read_xml'

    xml = fields.Binary('XML', required=True, filters='*.xml')
    filename_xml = fields.Char()
    pdf = fields.Binary('PDF', required=True, filters='*.pdf')
    filename_pdf = fields.Char()

    def get_dic(self, xml):
        if xml:
            dict_data = dict(xmltodict.parse(base64.decodestring(
                xml)).get('cfdi:Comprobante', {}))
            dic = dict_data
        return dic

    def get_taxes(self, dic):
        xml_taxes, odoo_taxes = [], []
        
        tras = dic.get('cfdi:Impuestos', {}).get(
            'cfdi:Traslados', {}).get("cfdi:Traslado", {})
        dic_tax = {
            'base': float(tras.get('@Base', 0.00)),
            'importe': float(tras.get('@Importe', 0.00)),
            'tasa': tras.get('@TasaOCuota', ''),
            'tipo': tras.get('@TipoFactor', ''),
            'impuesto': tras.get('@Impuesto', 0.00),
        }
        if dic_tax:
            xml_taxes.append(dic_tax)

        ret = dic.get('cfdi:Impuestos', {}).get(
            'cfdi:Retenciones', {}).get("cfdi:Retencion", {})
        dic_tax2 = {
            'base': float(ret.get('@Base', 0.00)),
            'importe': float(ret.get('@Importe', 0.00)),
            'tasa': ret.get('@TasaOCuota', ''),
            'tipo': ret.get('@TipoFactor', ''),
            'impuesto': ret.get('@Impuesto', 0.00),
        }
        if dic_tax2['base']:
            xml_taxes.append(dic_tax2)
        if len(xml_taxes):
            for tax in xml_taxes:
                tax_id = self.env['account.tax'].search(
                    [('amount', '=', float_round(
                        float(tax['tasa']) * 100, 4)),
                     ('type_tax_use', '=', 'purchase')
                     ])
                odoo_taxes.append(tax_id)
        
        total_traslados = float(dic.get('cfdi:Impuestos', {})\
            .get('@TotalImpuestosTrasladados', 0.0))
        total_retenidos = float(dic.get('cfdi:Impuestos', {})\
            .get('@TotalImpuestosRetenidos', 0.0))
        
        return odoo_taxes, (total_traslados - total_retenidos)

    def _check_filename_xml(self):
        for rec in self:
            if rec.xml:
                tmp = rec.filename_xml.split('.')
                ext = tmp[len(tmp)-1]
                if ext != 'xml':
                    raise ValidationError(
                        _("El archivo debe tener una extensión"
                          " .xml y sólo contener un punto (.) en el nombre"
                          " del archivo!"))

    def _check_filename_pdf(self):
        for rec in self:
            if rec.pdf:
                tmp = rec.filename_pdf.split('.')
                ext = tmp[len(tmp)-1]
                if ext != 'pdf':
                    raise ValidationError(
                        _("El archivo debe tener una extensión"
                          " .pdf y sólo contener un punto (.) en el nombre"
                          " del archivo!"))

    def do_validate(self):
        uuid = False
        for rec in self:
            if self.env.context.get('active_model') != 'hr.expense' or not \
                    self.env.context.get('active_ids'):
                raise UserError(_('El modelo activo no es hr.expense!'))
            active_ids = self.env.context.get('active_ids', False)
            if len(active_ids) > 1:
                raise UserError(_('Sólo puede cargar un documento a la vez!'))
            rec._check_filename_xml()
            rec._check_filename_pdf()
            attachment_ids = self.env['ir.attachment'].search([
                ('res_model','=', 'hr.expense'),
                ('res_id', '=', active_ids[0]),
                ])
            if len(attachment_ids) > 2:
                raise UserError(_("Usted no puede adjuntar más de 2 documentos al gasto!"))
            
            xml_binary = rec.xml
            if xml_binary:
                xml_bytes = base64.b64decode(
                    xml_binary)  # decode binary - bytes
                xml_bytes = xml_bytes.decode('utf-8')
                # split the string "xml_bytes" from 'UUID'
                try:
                    tipo_comprobante = xml_bytes.split("TipoDeComprobante", 1)[1][2:3]
                    if tipo_comprobante != 'I':
                        raise UserError(_("El XML adjunto no es de tipo Ingreso"))
                    xml_reduce = xml_bytes.split("UUID", 1)[1]
                    # reduce the string 'xml_reduce' and get the
                    # 37 character from 'UUID'
                    uuid = xml_reduce[2:38]
                except Exception as e:
                    raise ValidationError(_("Error el procesar el XML  contacte a su administrador %r" % e))
            
            if uuid:
                expense_id = self.env['hr.expense'].browse(active_ids)
                expense_id.l10n_mx_edi_cfdi_uuid = uuid
                expense_id.reference = uuid

                attachment_docs = self.env['ir.attachment'].search([
                    ('res_model', '=', 'hr.expense'), '|',
                    ('name', '=', "{0}.xml".format(uuid)),
                    ('name', '=', "{0}.pdf".format(uuid)),
                ])
                # verificando documentos repetidos en Gastos compartidos.
                if len(attachment_docs) > 0 and expense_id.tipo_factura is 'o':
                    raise UserError(_(u"El UUID seleccionado ya quedó registrado anteriormente!"))
                
                if not self.env.context.get('from_email', False):
                    # Generar adjuntos solo cuando la carga sea manual
                    filename = "{0}.xml".format(uuid)
                    ctx = self.env.context.copy()
                    ctx.pop('default_type', False)
                    attachment_id = self.env['ir.attachment'].with_context(
                        ctx).create({
                            'name': filename,
                            'res_id': expense_id.id,
                            'res_model': 'hr.expense',
                            'datas': rec.xml,
                            'description': 'Gasto {0}'.format(expense_id.name),
                        })
                    expense_id.message_post(
                        body=_('Document generated'),
                        attachment_ids=[attachment_id.id])
                    filename = "{0}.pdf".format(uuid)
                    pdf_id = self.env['ir.attachment'].with_context(
                        ctx).create({
                            'name': filename,
                            'res_id': expense_id.id,
                            'res_model': 'hr.expense',
                            'datas': rec.pdf,
                            'description': 'Gasto {0}'.format(expense_id.name),
                        })
                    expense_id.message_post(
                        body=_('Documento generado'),
                        attachment_ids=[pdf_id.id])

                # Search date, supplier, vat, subtotal and taxes
                tfd = self.get_dic(rec.xml)
                subtotal = float(tfd.get('@SubTotal', 0))
                date_string = tfd.get('@Fecha', None)
                supplier_xml = tfd.get('cfdi:Emisor', {})
                supplier_name = supplier_xml.get('@Nombre', '')
                supplier_rfc = supplier_xml.get('@Rfc', '')
                date_invoice = datetime.strptime(
                    date_string.replace('T', ' '), "%Y-%m-%d %H:%M:%S")
                expense_id.xml_date = date_invoice
                expense_id.unit_amount = round(subtotal, 2)
                odoo_taxes, monto_traslados_menos_retenciones = self.get_taxes(tfd)
                expense_id.tax_ids = [(6, 0, odoo_taxes[0].mapped('id'))]
                expense_id.supplier_name = supplier_name
                expense_id.supplier_rfc = supplier_rfc
                expense_id.total = tfd.get('@Total', '0.0')
                # expense_id.monto_pagado = tfd.get('@Total', '0.0')
                expense_id.company_rfc = tfd.get('cfdi:Receptor', {}).get('@Rfc', '')
                expense_id.monto_impuestos = monto_traslados_menos_retenciones
                
                if expense_id.travel_id:
                    if not expense_id.travel_id.date_due:
                        raise ValidationError(
                            _("El viaje asignado no tiene una fecha límite de comprobación, por favor contacte a su administrador!!"))
                    if expense_id.travel_id.date_due <= expense_id.date:
                        raise ValidationError(
                            _("La fecha del gasto excede la fecha límite de comprobación!!"))
                    if expense_id.xml_date <= expense_id.travel_id.date_start or expense_id.xml_date >= expense_id.travel_id.date_end:
                        IrDefault = self.env['ir.default'].sudo()
                        ir_param = IrDefault.get(
                            'res.config.settings', 'ms_check_mode') or False
                        if ir_param:
                            raise ValidationError(
                                _("Usted no puede comprobar un XML que no está dentro del rango del viaje!!"))
                        else:
                            expense_id.message_post(body=_(
                                'Advertencia. \nEl comprobante que usted intenta comprobar no está dentro del rango del viaje!!'))

            else:
                raise UserError(_("El XML no tiene un formato correcto!"))
