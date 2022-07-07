# -*- coding:utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
from base64 import b64encode as encode
from zeep.client import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from odoo.tools import email_split
import re
import logging

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):

    _inherit = 'hr.expense'

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code(
            'hr.expense') or '/'
        vals['sequence'] = seq
        return super(HrExpense, self).create(vals)

    @api.model
    def _default_product_id(self):
        product_id = self.env['product.product'].sudo().search([
            ('type', '=', 'service'),
            ('can_be_expensed', '=', True)], limit=1)
        return product_id

    name = fields.Char(default='/')
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('can_be_expensed', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",  # noqa
        ondelete='restrict',
        default=lambda s: s._default_product_id())
    sequence = fields.Char(string='Secuencia', copy=False, readonly=True,
                           states={'draft': [('readonly', False)],
                                   'reported': [('readonly', True)],
                                   'refused': [('readonly', True)]})
    state = fields.Selection(selection_add=[('validated_by_sat', 'Validado SAT')])
    xml_date = fields.Date('Fecha del XML', readonly=True)
    l10n_mx_edi_cfdi_uuid = fields.Char('UUID', readonly=True)
    travel_id = fields.Many2one(comodel_name='ms.hr.expense.travel',
                                string='Viaje', required=False)

    _sql_constraints = [('l10n_mx_edi_cfdi_uuid', 'check(1=1)',
                         'Removing _sql_constraints for "l10n_mx_edi_cfdi_uuid" field')]

    validated_by_robot = fields.Boolean('Validado por robot', copy=False,
                                        readonly=True)
    total = fields.Char('Total del CFDI', readonly=True, copy=False)
    company_rfc = fields.Char('RFC del receptor', readonly=True, copy=False)
    supplier_rfc = fields.Char('RFC del proveedor', readonly=True, copy=False)
    supplier_name = fields.Char(
        'Nombre del proveedor', readonly=True, copy=False)
    active = fields.Boolean(default=True)
    incidencias = fields.Text('Incidencias SAT')
    monto_impuestos = fields.Float('Total impuestos')
    tipo_factura = fields.Selection([('o', 'Ordinaria'), ('c', 'Compartida')], string='Tipo de Factura', default='o')
    total_amount = fields.Monetary("Total", compute='_compute_amount', store=True, currency_field='currency_id',
                                   readonly=False)
    asiento_id = fields.Many2one('account.move', 'Asiento contable')
    
    @api.model
    def default_get(self, fields_list):
        res = super(HrExpense, self).default_get(fields_list)
        
        IrDefault = self.env['ir.default'].sudo()
        res['account_id'] = IrDefault.get('res.config.settings', 'cuenta_gastos_id')\
            or False
        res['payment_mode'] = 'company_account'
        return res

    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id', 'tipo_factura')
    def _compute_amount(self):
        for expense in self:
            expense.untaxed_amount = expense.unit_amount * expense.quantity
            taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id, expense.quantity,
                                                expense.product_id, expense.employee_id.user_id.partner_id)
            if expense.tipo_factura is 'o':
                #expense.total_amount = expense.total_amount = taxes.get('total_included')
                expense.total_amount = expense.total
            else:
                if expense.total_amount > 0:
                    continue
                else:
                    expense.total_amount = 0.0

    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id or expense.sheet_id.state == 'draft':
                expense.state = "draft"
            elif expense.sheet_id.state == "cancel":
                expense.state = "refused"
            elif expense.sheet_id.state == "approve" or expense.sheet_id.state == "post":
                expense.state = "approved"
            elif not expense.sheet_id.account_move_id:
                expense.state = "reported"
            else:
                expense.state = "done"

    def unlink(self):
        for record in self:
            if record.state not in ('draft') or record.validated_by_robot:
                raise UserError(
                    _('Usted no puede eliminar un gasto validado por el robot'))
        return super(HrExpense, self).unlink()

    def write(self, values):
        res = super(HrExpense, self).write(values)
        if self.travel_id:
            if not self.travel_id.date_due:
                raise ValidationError(
                    _("El viaje asignado no tiene una fecha límite de comprobación, por favor contacte a su administrador!!"))
        return res
    
    @api.onchange('product_id', 'company_id')
    def _onchange_product_id(self):
        if self.product_id:
            if not self.name:
                self.name = self.product_id.display_name or ''
            self.unit_amount = self.product_id.price_compute('standard_price')[self.product_id.id]
            self.product_uom_id = self.product_id.uom_id
            self.tax_ids = self.product_id.supplier_taxes_id\
                .filtered(lambda tax: tax.company_id == self.company_id)  # taxes only from the same company
    
    @api.depends('employee_id')
    def _compute_is_editable(self):
        is_account_manager = self.env.user.has_group('account.group_account_user') or self.env.user.has_group('account.group_account_manager')
        for expense in self:
            if expense.state in ['draft', 'validated_by_sat'] or expense.sheet_id.state in ['draft', 'submit']:
                expense.is_editable = True
            elif expense.sheet_id.state == 'approve':
                expense.is_editable = is_account_manager
            else:
                expense.is_editable = False

    def action_submit_expenses(self):
        for record in self:
            if record.travel_id:
                if not record.travel_id.date_due:
                    raise ValidationError(
                        _("El viaje asignado no tiene una fecha límite de comprobación, por favor contacte a su administrador!!"))
                if record.travel_id.date_due <= record.date:
                    raise ValidationError(
                        _("La fecha del gasto excede la fecha límite de comprobación!!"))
                if record.xml_date >= record.travel_id.date_start and record.xml_date <= record.travel_id.date_end:
                    IrDefault = self.env['ir.default'].sudo()
                    ir_param = IrDefault.get(
                        'res.config.settings', 'ms_check_mode') or False
                    if ir_param:
                        raise ValidationError(
                            _("Usted no puede comprobar un XML que no está dentro del rango del viaje!!"))
                    else:
                        self.message_post(body=_(
                            'Advertencia. \nEl comprobante que usted intenta comprobar no está dentro del rango del viaje!!'))
        
            if record.state != 'validated_by_sat':
                raise UserError('No puede crear un informe con facturas no validadas por el SAT')
            if record.sheet_id:
                raise UserError('No puede usar un gasto que ya ha sido reportado')
            if not record.product_id:
                raise UserError('No puede crear un informe de gastos sin producto')
        
        if len(self.mapped('employee_id')) != 1:
            raise UserError('No puede usar distintos empleados en el mismo informe de gastos')

        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account')
        return {
            'name': 'Nuevo informe de gastos',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'context': {
                'default_expense_line_ids': todo.ids,
                'default_company_id': self.company_id.id,
                'default_employee_id': self[0].employee_id.id,
                'default_name': todo[0].name if len(todo) == 1 else ''
            }
        }

    @api.constrains('l10n_mx_edi_cfdi_uuid')
    def _check_uuid(self):
        if self.l10n_mx_edi_cfdi_uuid and not re.match(
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",  # noqa
            self.l10n_mx_edi_cfdi_uuid):
            raise ValidationError("Por favor ingrese un formato de UUID "
                                  "válido!")

    def _create_sheet_from_expenses(self):
        res = super(HrExpense, self)._create_sheet_from_expenses()
        if any(expense.state not in ('draft','validated_by_robot','validated_by_sat') or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in self):
            raise UserError(_("You can not create report without product."))

        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account')
        sheet = self.env['hr.expense.sheet'].create({
            'company_id': self.company_id.id,
            'employee_id': self[0].employee_id.id,
            'name': todo[0].name if len(todo) == 1 else '',
            'expense_line_ids': [(6, 0, todo.ids)]
        })
        sheet._onchange_employee_id()
        return sheet
    
    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id and expense.currency_id != company_currency

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.address_home_id.commercial_partner_id.id

            #se cambio la linea original para tomar siempre el total completo
            amount = expense.total_amount 
            
            amount_currency = False
            if different_currency:
                amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'amount_currency': amount_currency if different_currency else 0.0,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id if different_currency else False,
            }
            move_line_values.append(move_line_src)
            total_amount += -move_line_src['debit'] or move_line_src['credit']
            total_amount_currency += -move_line_src['amount_currency'] if move_line_src['currency_id'] else (-move_line_src['debit'] or move_line_src['credit'])
            """
            aca estaban las lineas para generar el asiento de la cuenta de impuestos,
            se quitaron porque SAP tiene su propio proceso para calcular impuestos en
            las polizas
            """
            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency if different_currency else 0.0,
                'currency_id': expense.currency_id.id if different_currency else False,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
            
        return move_line_values_by_expense
    
    def action_move_create(self):
        """
        Sobreescribe para generar una poliza por cada gasto del informe
        """
        # obtener los valores por default que prepara odoo
        # es un dict donde cada key representa un gasto del informe
        move_line_values_by_expense = self._get_account_move_line_values()
        for expense in self:
            # crear el asiento contable
            move_vals = expense._prepare_move_values()
            move = self.env['account.move'].with_context(default_journal_id=move_vals['journal_id']).create(move_vals)

            # obtener partidas de la poliza
            move_line_values = move_line_values_by_expense[expense.id]

            # link move lines to move, and move to expense sheet, and move to expense
            move.write({'line_ids': [(0, 0, line) for line in move_line_values]})
            expense.sheet_id.asientos_contables_ids += move
            expense.asiento_id = move.id
            
            # validar el asiento
            move.post()
    
    def send_to_validate(self):
        missing = []
        if not self.l10n_mx_edi_cfdi_uuid:
            missing.append('Folio fiscal')
        if not self.supplier_rfc:
            missing.append('RFC del emisor')
        if not self.company_rfc:
            missing.append('RFC del receptor')
        if not self.total:
            missing.append('Total del comprobante')
            
        if len(missing):
            msg = 'No se encontraron los campos:'
            msg += '\n * '.join(missing)
            msg += '\nCompruebe que los archivos hayan sido correctamente subidos'
            raise UserError(msg)
        
        cfdi_data = '?id=%s&re=%s&rr=%s&tt=%s' % (self.l10n_mx_edi_cfdi_uuid, self.supplier_rfc,
                                            self.company_rfc, self.total)
        client = Client('https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc', transport=Transport(cache=SqliteCache()))
        try:
            result = client.service.Consulta(expresionImpresa=cfdi_data)
            if result.Estado.lower() == 'vigente':
                self.incidencias = 'El comprobante de gastos ha sido procesado exitosamente.'
                self.validated_by_robot = True
                self.state = 'validated_by_sat'
            else:
                self.incidencias = 'El comprobante de gastos no fue encontrado en el SAT - %s' % result.Estado
                self.validated_by_robot = False
        except Exception as e:
            self.incidencias = str(e)
            self.validated_by_robot = False
            raise UserError("Ocurrio un error mientras se realizaba la validación %s" % str(e))
            
    @api.model
    def _message_new(self, msg_dict, custom_values=None):
        # Este metodo se encarga de crear el registro nuevo de hr.expense
        # a partir del email. Solamente se sobreescribe para quitar el envio
        # de correo de registro exitoso 
        email_address = email_split(msg_dict.get('email_from', False))[0]

        employee = self.env['hr.employee'].search([
            '|',
            ('work_email', 'ilike', email_address),
            ('user_id.email', 'ilike', email_address)
        ], limit=1)

        expense_description = msg_dict.get('subject', '')

        if employee.user_id:
            company = employee.user_id.company_id
            currencies = company.currency_id | employee.user_id.company_ids.mapped('currency_id')
        else:
            company = employee.company_id
            currencies = company.currency_id

        if not company:  # ultimate fallback, since company_id is required on expense
            company = self.env.company

        product, price, currency_id, expense_description = self._parse_expense_subject(expense_description, currencies)
        vals = {
            'employee_id': employee.id,
            'name': expense_description,
            'unit_amount': price,
            'product_id': product.id if product else None,
            'product_uom_id': product.uom_id.id,
            'tax_ids': [(4, tax.id, False) for tax in product.supplier_taxes_id],
            'quantity': 1,
            'company_id': company.id,
            'currency_id': currency_id.id
        }

        account = product.product_tmpl_id._get_product_accounts()['expense']
        if account:
            vals['account_id'] = account.id
        
        expense = super(HrExpense, self).message_new(msg_dict, dict(custom_values or {}, **vals))
        # Este es el unico cambio: el correo de exito no se envia hasta despues de validar el XML
        return expense
    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *,
                     body='', subject=None, message_type='notification',
                     email_from=None, author_id=None, parent_id=False,
                     subtype_id=False, partner_ids=None,
                     attachments=None, attachment_ids=None,
                     add_sign=True, record_name=False,
                     **kwargs):
        # Este metodo se invoca despues de crear el hr.expense, y es en donde se crean los adjuntos
        new_msg = super(HrExpense, self).message_post(body=body, subject=subject, message_type=message_type, 
                                            email_from=email_from, author_id=author_id, parent_id=parent_id, 
                                            subtype_id=subtype_id, partner_ids=partner_ids, 
                                            attachments=attachments, 
                                            attachment_ids=attachment_ids, add_sign=add_sign, 
                                            record_name=record_name, **kwargs)
        if not self.env.context.get('manual', False):
            return new_msg
        # Inicio de modificaciones: Aplicar las validaciones del wizard
        # Verificar existencia de adjuntos
        attach_id = self.env['ir.attachment'].search([('res_model', '=', self._name), 
                                                      ('res_id', '=', self.id)])
        if not len(attach_id):
            # Sin adjuntos?
            msg = 'No se encontraron archivos adjuntos para validar. Puede adjuntarlos manualmente.'
            super(HrExpense, self).message_post(body=msg)
        else:
            # Verificar que haya XML y PDF
            xml_data = attach_id.filtered(lambda l: l.name.endswith('.xml'))
            pdf_data = attach_id.filtered(lambda l: l.name.endswith('.pdf'))
            
            error_msg = False
            if not len(xml_data):
                error_msg = 'No se encontró archivo XML adjunto para validar. Puede subirlo manualmente.'
            elif not len(pdf_data):
                error_msg = 'No se encontró archivo PDF adjunto. Puede subirlo manualmente.'
            else:
                # Reusar validaciones existentes en el asistente
                attach_wizard = self.env['hr.expense.read.xml'].create({
                                    'xml' : xml_data.datas,
                                    'filename_xml' : xml_data.name,
                                    'pdf' : pdf_data.datas,
                                    'filename_pdf' : pdf_data.name
                                })
                try:
                    # Todo bien con validaciones locales
                    attach_wizard\
                        .with_context(active_model=self._name, active_ids=self.ids, from_email=True)\
                        .do_validate()
                except Exception as ex:
                    error_msg = str(ex)
                    super(HrExpense, self).message_post(body=error_msg)
            
            if error_msg:
                # Dejar registro del error encontrado
                super(HrExpense, self).message_post(body=error_msg)
            else:
                self.send_to_validate()
                
                # Verificar estatus de validacion SAT
                if 'exitosamente' in self.incidencias:
                    dict_values = dict(**kwargs)
                    self._send_expense_success_mail(dict_values, self)
                else:
                    # Si no fue valido, enviar un correo informando
                    rejected_type_id = self.env.ref('hr_expense.mt_expense_refused')
                    self.message_post(body='Su comprobante ha sido rechazado', 
                                      subtype_id = rejected_type_id.id,
                                      reason=self.incidencias)
                    
        return new_msg

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self):
        for record in self:
            if record.res_model == 'hr.expense':
                expense_id = self.env['hr.expense'].browse(int(record.res_id))
                if expense_id.state in ['validated_by_sat', 'sent_to_robot']:
                    raise ValidationError(_("No se puede eliminar los documentos de un gasto validado"))
                
                # Si se elimina XML, borrar tambien los datos fiscales del gasto
                if record.name.endswith('xml'):
                    expense_id.write({
                        'xml_date' : False,
                        'reference' : False,
                        'l10n_mx_edi_cfdi_uuid' : False,
                        'supplier_rfc' : False,
                        'supplier_name' : False,
                        'company_rfc' : False
                    })
        return super(IrAttachment, self).unlink()
