# -*- coding:utf-8 -*-
# @author Carlos A. Garcia

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class HrUploadDoc(models.TransientModel):
    _name = 'hr.upload.doc'

    doc = fields.Binary('Documento', required=True)
    filename_doc = fields.Char()

    def _check_filename_pdf(self):
        for rec in self:
            if rec.doc:
                tmp = rec.filename_doc.split('.')
                ext = tmp[len(tmp)-1]
                if ext != 'pdf':
                    raise ValidationError(_("El archivo debe tener una extensión .pdf y sólo contener un punto (.) en "
                                            "el nombre del archivo!"))

    def do_attach(self):
        for rec in self:
            active_ids = self.env.context.get('active_ids', False)
            model = self.env.context.get('active_model')
            if len(active_ids) > 1:
                raise UserError(_('Sólo puede cargar un documento a la vez!'))
            # rec._check_filename_pdf()
            if self.filename_doc:
                attachment_docs = self.env['ir.attachment'].search([('res_model', '=', model),
                                                                    ('name', '=', self.filename_doc)])
                # verificando documentos repetidos.
                if len(attachment_docs) > 0:
                    raise UserError(_(u"El documento seleccionado ya quedó registrado anteriormente!"))
                obj_id = self.env[model].browse(active_ids)
                # Generar adjuntos solo cuando la carga sea manual
                ctx = self.env.context.copy()
                ctx.pop('default_type', False)
                doc_id = self.env['ir.attachment'].with_context(ctx).create({
                        'name': self.filename_doc,
                        'res_id': obj_id.id,
                        'res_model': model,  # 'ms.hr.expense.travel',
                        'datas': rec.doc,
                        'description': 'Gasto {0}'.format(obj_id.name),
                    })
                obj_id.message_post(body=_('Documento adjuntado'), attachment_ids=[doc_id.id])
            else:
                raise UserError(_("Debe seleccionar un archivo para adjuntar!"))
