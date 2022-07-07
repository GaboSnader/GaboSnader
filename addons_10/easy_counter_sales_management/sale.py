# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################


from openerp import models, fields, api, _
from datetime import time, datetime
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import time
from odoo.tools.translate import _
from odoo.tools.safe_eval import safe_eval

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}


class AccountInvoiceRefund(models.TransientModel):
    _name = 'account.invoice.refund'
    _inherit ='account.invoice.refund'

    order_id = fields.Many2one('sale.order', 'Pedido Venta')
    refund_clean = fields.Boolean('Nota Limpia', help='No incluye ningun Producto', )


    @api.onchange('filter_refund')
    def onchange_filter_refund(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        self.env.cr.execute("""
            select sale_order_line.order_id from sale_order_line_invoice_rel 
                join account_invoice_line on sale_order_line_invoice_rel.invoice_line_id =  account_invoice_line.id
                join sale_order_line on sale_order_line.id = sale_order_line_invoice_rel.order_line_id
                and account_invoice_line.invoice_id in %s
                group by sale_order_line.order_id

            """, (tuple(active_ids),))
        cr_res = self.env.cr.fetchall()
        order_list = []
        domain = {}
        if cr_res:
            order_list = [x[0] for x in cr_res if x]
            if order_list:
                domain.update(
                    {
                        'order_id':[
                                      ('id','in',tuple(order_list))]
                    }) 
                return {'domain': domain}
        else:
            domain.update(
                    {
                        'order_id':[
                                      ('id','in',())]
                    }) 
            return {'domain': domain}

    @api.multi
    def compute_refund(self, mode='refund'):
        for rec in self:
            if mode != 'refund':
                return super(AccountInvoiceRefund, self).compute_refund(mode)
            if rec.order_id == False and not rec.refund_clean:
                return super(AccountInvoiceRefund, self).compute_refund(mode)
            if rec.order_id and rec.refund_clean:
                raise UserError ("Error!\nNo puede seleccioanr un Pedido y la Nota en Limpio.\nSelecciona una opcion.")  
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False

        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise UserError(_('Cannot refund draft/proforma/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise UserError(_('Cannot refund invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                refund = inv.with_context(order_id = form.order_id).refund(form.date_invoice, date, description, inv.journal_id.id)
                if form.refund_clean:
                    refund.invoice_line_ids.unlink()
                refund.compute_taxes()


                created_inv.append(refund.id)
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.action_invoice_open()
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                            to_reconcile_lines.reconcile()
                    if mode == 'modify':
                        invoice = inv.read(
                                    ['name', 'type', 'number', 'reference',
                                    'comment', 'date_due', 'partner_id',
                                    'partner_insite', 'partner_contact',
                                    'partner_ref', 'payment_term_id', 'account_id',
                                    'currency_id', 'invoice_line_ids', 'tax_line_ids',
                                    'journal_id', 'date'])
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
                        invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                        })
                        for field in ('partner_id', 'account_id', 'currency_id',
                                         'payment_term_id', 'journal_id'):
                                invoice[field] = invoice[field] and invoice[field][0]
                        inv_refund = inv_obj.create(invoice)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = (inv.type in ['out_refund', 'out_invoice']) and 'action_invoice_tree1' or \
                         (inv.type in ['in_refund', 'in_invoice']) and 'action_invoice_tree2'
                # Put the reason in the chatter
                subject = _("Invoice refund")
                body = description
                refund.message_post(body=body, subject=subject)
        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('state', 'invoice_line_ids')
    def _get_orders_rel(self):
        for invoice in self:
            if type(invoice.id) == int:
                self.env.cr.execute("""
                    select sale_order_line.order_id from sale_order_line_invoice_rel 
                        join account_invoice_line on sale_order_line_invoice_rel.invoice_line_id =  account_invoice_line.id
                        join sale_order_line on sale_order_line.id = sale_order_line_invoice_rel.order_line_id
                        and account_invoice_line.invoice_id = %s
                        group by sale_order_line.order_id

                    """, (invoice.id,))
                cr_res = self.env.cr.fetchall()
                order_list = []
                if cr_res:
                    order_list = [x[0] for x in cr_res if x]
                # print "#### PEDIDOS RELACIONADOS >>> ",order_list
                invoice.update({
                    'sale_ids': order_list,
                })

    sale_ids = fields.Many2many("sale.order", string='Pedidos', compute="_get_orders_rel", readonly=True, copy=False)
   
    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
        new_invoices = self.browse()
        context = self._context
        for invoice in self:
            # create the new invoice
            values = self._prepare_refund(invoice, date_invoice=date_invoice, date=date,
                                    description=description, journal_id=journal_id)
            if 'order_id' in context:
                new_lines = []
                order_id = context['order_id']
                if order_id:
                    for line in order_id.order_line:
                        line_vals = line._prepare_invoice_line(line.product_uom_qty)
                        new_lines.append((0,0,line_vals))
                    values.update({'invoice_line_ids':new_lines})
            refund_invoice = self.create(values)
            invoice_type = {'out_invoice': ('customer invoices refund'),
                'in_invoice': ('vendor bill refund')}
            message = _("This %s has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a>") % (invoice_type[invoice.type], invoice.id, invoice.number)
            refund_invoice.message_post(body=message)
            new_invoices += refund_invoice
        return new_invoices

    @api.multi
    def reconcile_payments_sale_order(self):
        payment_obj = self.env['account.payment']
        for invoice in self:
            self.env.cr.execute("""
                select sale_order_line.order_id from sale_order_line_invoice_rel 
                    join account_invoice_line on sale_order_line_invoice_rel.invoice_line_id =  account_invoice_line.id
                    join sale_order_line on sale_order_line.id = sale_order_line_invoice_rel.order_line_id
                    and account_invoice_line.invoice_id = %s
                    group by sale_order_line.order_id

                """, (invoice.id,))
            cr_res = self.env.cr.fetchall()
            order_list = []
            if cr_res:
                order_list = [x[0] for x in cr_res if x]
            # print "#### PEDIDOS RELACIONADOS >>> ",order_list
            if not order_list:
                self.env.cr.execute("""
                    select sale_id from account_invoice_sale_rel
                        where invoice_id = %s;
                    """, (invoice.id,))
                cr_res = self.env.cr.fetchall()
                order_list = []
                if cr_res:
                    order_list = [x[0] for x in cr_res if x]
                if not order_list:
                    raise UserError(_("Error!\nNo existen registros de Pedidos a Conciliar."))
            for order in self.env['sale.order'].browse(order_list):
                if order.total_payment == False and order.payment_exception == False:
                    raise UserError(_("Error!\nEl Pedido %s no se encuentra pagado en su totalidad. \nPuede activar la Excepcion de Pago en el Pedido o Pedidos Origen." % order.name))

            ### Conciliando ####
            # amls_to_reconcile = self.env['account.move.line']
            # payment_ids = payment_obj.search([('sale_order_id','in',tuple(order_list))])
            
            # print "#### PAYMENT IDS >>> ",payment_ids
            if len(order_list) > 1:
                amls_to_reconcile = self.env['account.move.line']
                ### Optimizacion por Querys ###
                self.env.cr.execute("""
                    select id from account_payment
                        where sale_order_id in %s;
                    """,(tuple(order_list),))
                cr_res = self.env.cr.fetchall()
                payment_list = [x[0] for x in cr_res]
                if not payment_list:
                    raise UserError(_("Error!\nNo existen Pagos para Conciliar."))

                self.env.cr.execute("""
                    select partner_id from account_payment
                        where sale_order_id in %s
                        and partner_id != %s;
                    """,(tuple(order_list),invoice.partner_id.id))
                cr_res = self.env.cr.fetchall()
                partner_payment_list = []
                if cr_res:
                    partner_payment_list = [x[0] for x in cr_res]
                if partner_payment_list:
                    self.env.cr.execute("""
                        update account_payment
                            set partner_id = %s
                            where id in %s;
                        """,(invoice.partner_id.id,tuple(payment_list),))

                    self.env.cr.execute("""
                        update account_move_line
                            set partner_id = %s
                            where payment_id in %s;
                        """,(invoice.partner_id.id,tuple(payment_list),))

                    self.env.cr.execute("""
                        update account_move
                            set partner_id = %s
                            where id in (select move_id from
                                account_move_line where payment_id in %s);
                        """,(invoice.partner_id.id,tuple(payment_list),))

                payment_move_line_to_reconcile = []
                self.env.cr.execute("""
                    select account_move_line.id from account_move_line
                        join account_account on account_account.id = account_move_line.account_id
                        where account_move_line.payment_id in %s
                            and account_move_line.reconciled = False
                            and account_account.internal_type in ('payable', 'receivable');
                    """,(tuple(payment_list),))
                cr_res = self.env.cr.fetchall()
                if cr_res:
                    payment_move_line_to_reconcile = [x[0] for x in cr_res]

                invoice_move_line_to_reconcile = []
                self.env.cr.execute("""
                    select account_move_line.id from account_move_line
                        join account_account on account_account.id = account_move_line.account_id
                        where account_move_line.move_id = %s
                            and account_move_line.reconciled = False
                            and account_account.internal_type in ('payable', 'receivable');
                    """,(invoice.move_id.id,))
                cr_res = self.env.cr.fetchall()
                if cr_res:
                    invoice_move_line_to_reconcile = [x[0] for x in cr_res]

                amls_to_reconcile = amls_to_reconcile.browse(payment_move_line_to_reconcile+invoice_move_line_to_reconcile)

                amls_to_reconcile.reconcile(writeoff_acc_id=False, writeoff_journal_id=False)
            else:
                ## Esto es para la version Normal con metodos de Odoo ###
                amls_to_reconcile = self.env['account.move.line']
                payment_ids = payment_obj.search([('sale_order_id','in',tuple(order_list))])
                
                for payment in payment_ids:
                    # Cambiando el Partner ##
                    partner_list = [x.partner_id.id for x in payment.move_line_ids if x.partner_id]
                    partner_list = list(set(partner_list))
                    if partner_list:
                        if invoice.partner_id.id != partner_list[0]:
                            ## Cambiando el partner en las Partidas #
                            for mv_line in payment.move_line_ids:
                                mv_line.write({'partner_id':invoice.partner_id.id})
                                mv_line.move_id.write({'partner_id':invoice.partner_id.id})
                            payment.write({'partner_id':invoice.partner_id.id})
                            # self.env.cr.execute("""
                            #     update account_move_line set partner_id=%s where id in %s;
                            #     """,(invoice.partner_id.id, tuple(move_line_list_ids)))
                            # self.env.cr.execute("""
                            #     update account_move set partner_id=%s where id in %s;
                            #     """,(invoice.partner_id.id, tuple(move_list_ids)))
                    ### Conciliando ####
                    # move_line_ids
                    for move_line in payment.move_line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable')):
                        amls_to_reconcile += move_line
                amls_to_reconcile += invoice.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
                amls_to_reconcile.reconcile(writeoff_acc_id=False, writeoff_journal_id=False)



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _name = 'sale.order.line'

    image_medium = fields.Binary(
        "Imagen Producto", related='product_id.image_medium', store=True)
    # image_small = fields.Binary('Imagen Producto')


    @api.model # Self, cr, uid, ids, context
    def create(self, vals):
        if 'order_id' in vals:
            order_id = vals['order_id']
            order_br = self.env['sale.order'].browse(order_id)
            if order_br.state in ('sale','done', 'cancel'):
                raise UserError(_("Error!\n\nNo puedes añadir Productos a un Pedido en Proceso."))
        res = super(SaleOrderLine, self).create(vals)
        return res

    # @api.multi
    # @api.onchange('product_id')
    # def product_id_change(self):
    #     res_prod = super(SaleOrderLine, self).product_id_change()
    #     if self.product_id:
    #         self.image_small = self.product_id.image_small

    #     return res_prod

    # @api.multi
    # @api.constrains('order_id')
    # def _restrict_order_open(self):

class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit ='account.payment'

    sale_order_id = fields.Many2one('sale.order','Pedido de Venta', copy=False)
    easy_refund = fields.Float('Cambio')

    @api.model # Self, cr, uid, ids, context
    def create(self, vals):
        if 'sale_order_id' in vals:
            order_id = vals['sale_order_id']
            order_br = self.env['sale.order'].browse(order_id)
            if order_br.total_payment:
                raise UserError(_("Error!\nEl Pedido ya se encuentra en estado Pagado"))
        res = super(AccountPayment, self).create(vals)
        return res

    @api.onchange('easy_refund','sale_order_id','amount')
    def on_change_easy_refund(self):
        if self.sale_order_id:
            amount_to_pay = self.sale_order_id.amount_payment + self.amount
            if amount_to_pay > self.sale_order_id.amount_total:
                #self.amount = self.sale_order_id.amount_total
                easy_refund = amount_to_pay - self.sale_order_id.amount_total
                self.easy_refund = easy_refund
                self.sale_order_id.write({'easy_refund':easy_refund})

    @api.model
    def default_get(self, fields2):
        context = dict(self._context)
        active_model = context['active_model'] if 'active_model' in context else ""
        if active_model == 'sale.order':
            context['default_invoice_ids'] = []
            rec = {}
            active_id = context['active_id']
            sale_br = self.env['sale.order'].browse(active_id)
            amount_residual = sale_br.amount_total-sale_br.amount_payment

            rec['communication'] = sale_br.name
            rec['currency_id'] = sale_br.pricelist_id.currency_id.id
            rec['payment_type'] = 'inbound'
            rec['partner_type'] = 'customer'
            rec['partner_id'] = sale_br.partner_id.id
            rec['amount'] = amount_residual
            rec['invoice_ids'] = []
            rec['sale_order_id'] = sale_br.id
            rec['state'] = 'draft'
            rec['payment_date'] = fields.Date.context_today(self)
            return rec
        rec = super(AccountPayment, self).default_get(fields2)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['communication'] = invoice['reference'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['residual']
        return rec

    @api.multi
    def post(self):
        for rec in self:
            ## Validando Pedidos Pagados ##
            if rec.sale_order_id:
                if rec.sale_order_id.total_payment:
                    raise UserError(_("Error!\nEl Pedido ya se encuentra en estado Pagado"))
                else:
                    amount_to_pay = rec.sale_order_id.amount_payment + rec.amount
                    if amount_to_pay > rec.sale_order_id.amount_total:
                        amount_to_write = rec.sale_order_id.amount_total - rec.sale_order_id.amount_payment
                        rec.write({'amount': amount_to_write})

                    #     raise UserError(_("Error!\nEl monto del Pago supera el monto adeudado."))

            if rec.invoice_ids:
                for inv in rec.invoice_ids:
                    if inv.sale_ids:
                        for sale in inv.sale_ids:
                            if sale.total_payment:
                                raise UserError(_("Error!\nLa Factura tiene Pagos Pendientes a conciliar de Ordenes de Venta, por ello es necesario Conciliar mediante el Boton Conciliar Pagos Ventas."))

        res = super(AccountPayment, rec).post()
        for rec in self:
            if rec.sale_order_id:
                amount_payment = rec.amount+rec.sale_order_id.amount_payment
                rec.sale_order_id.write({'amount_payment':amount_payment})
                amount_payment = amount_payment+0.01
                if amount_payment >= rec.sale_order_id.amount_total:
                    rec.sale_order_id.write({'total_payment':True, 'user_payment_register_id': self.env.user.id})      
        return res

    @api.multi
    def cancel(self):
        res = super(AccountPayment, self).cancel()
        for rec in self:
            if rec.sale_order_id:
                amount_payment = rec.sale_order_id.amount_payment - rec.amount
                vals = {
                         'total_payment': False,
                         'amount_payment': amount_payment,
                        }
                rec.sale_order_id.write(vals)
        return res

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id','sale_order_id')
    def _compute_destination_account_id(self):
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
        if self.sale_order_id:
            self.destination_account_id = self.partner_id.property_account_receivable_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('Transfer account not defined on the company.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            if self.partner_type == 'customer':
                self.destination_account_id = self.partner_id.property_account_receivable_id.id
            else:
                self.destination_account_id = self.partner_id.property_account_payable_id.id


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'

    @api.depends('state', 'amount_payment', 'total_payment')
    def _get_payments(self):

        for order in self:
            payment_ids = []
            payment_ids = self.env['account.payment'].search([('sale_order_id','=',order.id)])
            payment_ids = [x.id for x in payment_ids if payment_ids]
        
            order.update({
                'payment_count': len(payment_ids),
            })

    amount_payment = fields.Float('Monto Pagado', copy=False)
    total_payment = fields.Boolean('Pagado', copy=False)
    
    payment_exception = fields.Boolean('Excepcion Pago', copy=False)

    payment_count = fields.Integer(string='# of Pagos', compute='_get_payments', readonly=True)

    # product_on_id = fields.Many2one('product.product','Producto', required=False,)
    # product_qty =  fields.Integer('Cantidad', default=1)

    product_on_read = fields.Char('Lectura Codigo Barras', required=False, help="""Ingresa el Codigo del Producto Automaticamente se Agregara como linea tomando El precio del producto y su unidad de Medida
        Podemos Agregar los Siguientes Comodines:
            - Si queremos agregar el Producto y la Cantidad a la Vez ponemos el Codigo del Producto + Cantidad, es importante poner el simbolo + despues del Producto'""" )

    easy_refund = fields.Float('Cambio')

    re_invoiced = fields.Boolean('Refacturado')

    user_payment_register_id = fields.Many2one('res.users','Cajero')

    @api.multi
    def re_inviced_public(self):
        for rec in self:
            invoice_obj = self.env['account.invoice']
            invoice_line_obj = self.env['account.invoice.line']
            rec.re_invoiced = True
            invoice_vals = rec._prepare_invoice()
            invoice_id = invoice_obj.create(invoice_vals)
            for line in rec.order_line:
                invoice_line_vals = line._prepare_invoice_line(line.product_uom_qty)
                invoice_line_id = invoice_line_obj.create(invoice_line_vals)
                invoice_line_id.write({'invoice_id': invoice_id.id})
            invoice_id.compute_taxes()

            return {
                        'name': _('Refacturacion del Pedido %s' % rec.name),
                        'view_mode': 'form',
                        'view_id': self.env.ref('account.invoice_form').id,
                        'res_model': 'account.invoice',
                        'context': "{}", # self.env.context
                        'type': 'ir.actions.act_window',
                        'res_id': invoice_id.id,
                    }
                    
                    


    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for rec in self:
            payment_ids = self.env['account.payment'].search([('sale_order_id','=',rec.id)])
            if payment_ids:
                for payment in payment_ids:
                    if payment.state not in ( 'draft','cancel' ):
                        raise UserError(_("Error!\nNo puedes cancelar el Pedido, primero debes cancelar los Pagos Relacionados."))
            rec.write({'total_payment':False,'amount_payment': 0.0})
        return res

    @api.multi
    def action_view_payments(self):
        payment_ids = []
        payment_ids = self.env['account.payment'].search([('sale_order_id','=',self.id)])
        payment_ids = [x.id for x in payment_ids if payment_ids]
        
        if len(payment_ids) > 1:
            return {
                'domain': [('id', 'in', payment_ids)],
                'name': _('Pagos del Pedido %s' % self.name),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'account.payment',
                'type': 'ir.actions.act_window'
                }
        else:
            return {
                'name': _('Pago del Pedido %s' % self.name),
                'view_mode': 'form',
                'res_model': 'account.payment',
                'type': 'ir.actions.act_window',
                'res_id': payment_ids[0],
                }
       
    @api.onchange('partner_id', 'product_on_read', 'order_line','pricelist_id')
    def on_change_load_products(self):

        product_obj = self.env['product.product']
        salesman_obj = self.env['res.users']
        partner_obj = self.env['res.partner']
        partner = partner_obj.browse(self.partner_id)
        lines = [x.id for x in self.order_line]
        if not self.product_on_read:
            return {}

        qty_product = 1

        if self.product_on_read:
            if '+' in self.product_on_read:
                try:
                    product_on_read = self.product_on_read.split("+")
                    qty_product_str = product_on_read[1]
                    qty_product = float(qty_product_str)

                except:
                    raise UserError(_("Error!\nLa Informacion Introducida Contiene Errores. Verifique que el orden de la informacion sea como los siguientes ejemplos:\
                              \n -[Cantidad+CodigoProducto]"))

        product_on_read = self.product_on_read.split("+")
        default_code = product_on_read[0]
        if len(default_code) > 12:
            default_code = default_code[0:12]
        # product_search = product_obj.search([('default_code','=',default_code)])
        self.env.cr.execute("""
            select id from product_product where UPPER(default_code) = %s;
            """, (default_code.upper(),))
        cr_res = self.env.cr.fetchall()
        product_search = [x[0] for x in cr_res]
        if not product_search:
            self.env.cr.execute("""
                select id from product_product where UPPER(barcode) like %s;
                """, ('%'+default_code.upper()+'%',))
            cr_res = self.env.cr.fetchall()
            product_search = [x[0] for x in cr_res]
            if not product_search:
                raise UserError(_("Error!\nEl codigo [%s] no coincide con ninguna referencia de Producto." % default_code))

        product_id = product_search[0]
        product_br = product_obj.browse(product_search[0])
        if product_br.default_code:
            product_name = '['+product_br.default_code +']'+product_br.name
        else:
            product_name = product_br.name
        if product_br.property_account_income_id:
            account_id = product_br.property_account_income_id.id
        else:
            account_id = product_br.categ_id.property_account_income_categ_id.id
        # price = product_br.lst_price
        sale_order_line = self.env['sale.order.line']

        product_br_with_ctx = product_br.with_context(pricelist=self.pricelist_id.id)
        if self.pricelist_id and self.partner_id:
            # price = self.env['account.tax']._fix_tax_included_price(sale_order_line._get_display_price(product_br), product_br.taxes_id, [_w for _w in product_br.taxes_id] )
            price = product_br_with_ctx.price
        else:
            price = product_br.lst_price
        taxes_list = [_w.id for _w in product_br.taxes_id]

        if product_id:
            xline = (0,0,{
                    'product_id': product_id,
                    'name': product_name,
                    'tax_id': [(6, 0, taxes_list )],
                    'product_uom_qty': int(qty_product),
                    'price_unit': price,
                    'product_uom': product_br.uom_id.id,
                    # 'account_id': account_id,
                })
            lines.append(xline)

        self.update({'order_line': lines})
            
        self.product_on_read = False
        self.recalculate_prices()

    @api.multi
    def recalculate_prices(self):
        for record in self:
            if record.order_line:
                for line in record.order_line:
                    res = line.product_id_change()
                    res2 = line._onchange_discount()
                    #print "######### RES >>> ",res
                    #self.update(res)
        return True

    ### Reemplazamos Imprimir por el Ticket ###
    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env['report'].get_action(self, 'easy_counter_sales_management.template_easy_ticket')


class StockImmediateTransfer(models.TransientModel):
    _name = 'stock.immediate.transfer'
    _inherit = 'stock.immediate.transfer'

    @api.multi
    def process(self):
        self.ensure_one()
        if self.pick_id:
            if self.pick_id.sale_id:
                if self.pick_id.sale_id.total_payment == False:
                    if self.pick_id.sale_id.payment_exception == False:
                        raise UserError(_("Error!\nSolo puede entregarse la Mercancia si el Pedido esta Pagado."))
        res = super(StockImmediateTransfer, self).process()
        return res

    # def on_change_load_products(self, cr, uid, ids, company_id, partner_id, product_on_id, order_line, pricelist_id, context=None):
    #     # pos_line_obj = self.pool.get('pos.order.line')
    #     product_obj = self.pool.get('product.product')
    #     salesman_obj = self.pool.get('res.users')
    #     partner_obj = self.pool.get('res.partner')
    #     if partner_id:
    #         partner = partner_obj.browse(cr, uid, partner_id, context=None)
    #         lines = order_line

    #         fpos_obj = self.pool.get('account.fiscal.position')
    #         fpos = partner.property_account_position.id or False
    #         fpos = fpos and fpos_obj.browse(cr, uid, fpos, context=context) or False
    #         # tax_id = [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)])],

    #         if not product_on_id:
    #             return {}
    #         if '+' in product_on_id:
    #             try:
    #                 cod_product = product_on_id.split('+')[1]
    #                 qty_product = product_on_id.split('+')[0]
    #                 # print " CODIGO DEL VENDEDOR",sale_tpv_cod
    #                 product_id = product_obj.search(cr, uid, ['|',('default_code','=',cod_product),('ean13','=',cod_product)])
    #                 product_br = product_obj.browse(cr, uid, product_id, context=None)[0]
    #                 if product_br.default_code:
    #                     product_name = ' [ '+product_br.default_code +' ] '+product_br.name
    #                 else:
    #                     product_name = product_br.name
    #                 if product_id:
    #                     product_pricelist = 0.0
    #                     if not pricelist_id:
    #                         product_pricelist = product_br.list_price
    #                     else:
    #                         date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
    #                         product_pricelist = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
    #                                 product_id[0], int(qty_product) or 1.0, partner_id, {
    #                                     'uom': product_br.uom_id.id,
    #                                     'date': date_order,
    #                                     })[pricelist_id]

    #                     xline = (0,0,{
    #                             'product_id': product_id[0],
    #                             'name': product_name,
    #                             'tax_id': [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_br.taxes_id)])],
    #                             'product_uom_qty': int(qty_product),
    #                             'price_unit': product_pricelist,
    #                             'product_uom': product_br.uom_id.id,
    #                         })
    #                     lines.append(xline)
    #                 else:
    #                     warning = {
    #                                 'title': 'Error Captura!',
    #                                 'message': 'El Codigo Capturado no Encontro Ningun Producto en la Base de Datos, Codigo %s' % (cod_product,),
    #                             }
    #                     return {'value' : {'product_on_id':False,},'warning':warning}
    #             except:
    #                 warning = {
    #                         'title':'Error !',
    #                         'message':'La Informacion Introducida Contiene Errores Verificar que el orden de la informacion sea de los ejemplos:\
    #                          \n -[Cantidad+CodigoProducto]'}
    #                 return {'value' : {'product_on_id':False,},'warning':warning}
    #         else:
    #             try:
    #                 cod_product = product_on_id
    #                 qty_product = 1
    #                 # print " CODIGO DEL VENDEDOR",sale_tpv_cod
    #                 product_id = product_obj.search(cr, uid, ['|',('default_code','=',cod_product),('ean13','=',cod_product)])
    #                 product_br = product_obj.browse(cr, uid, product_id, context=None)[0]
    #                 if product_br.default_code:
    #                     product_name = ' [ '+product_br.default_code +' ] '+product_br.name
                    
    #                 else:
    #                     product_name = product_br.name
    #                 if product_id:
    #                     product_pricelist = 0.0
    #                     if not pricelist_id:
    #                         product_pricelist = product_br.list_price
    #                     else:
    #                         date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
    #                         product_pricelist = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
    #                                 product_id[0], int(qty_product) or 1.0, partner_id, {
    #                                     'uom': product_br.uom_id.id,
    #                                     'date': date_order,
    #                                     })[pricelist_id]
    #                     xline = (0,0,{
    #                             'product_id': product_id[0],
    #                             'name': product_name,
    #                             'tax_id': [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_br.taxes_id)])],
    #                             'product_uom_qty': int(qty_product),
    #                             'price_unit': product_pricelist,
    #                             'product_uom': product_br.uom_id.id,
    #                         })
    #                     lines.append(xline)
    #                 else:
    #                     warning = {
    #                                 'title': 'Error Captura!',
    #                                 'message': 'El Codigo Capturado no Encontro Ningun Producto en la Base de Datos, Codigo %s' % (cod_product,),
    #                             }
    #                     return {'value' : {'product_on_id':False,},'warning':warning}
    #             except:
    #                 warning = {
    #                         'title':'Error !',
    #                         'message':'La Informacion Introducida Contiene Errores Verificar que el orden de la informacion sea de los ejemplos:\
    #                          \n -[Cantidad+CodigoProducto]'}
    #                 return {'value' : {'product_on_id':False,},'warning':warning}

    #     else:
    #         lines = order_line

    #         tax_id = []

    #         if not product_on_id:
    #             return {}
    #         if '+' in product_on_id:
    #             try:
    #                 cod_product = product_on_id.split('+')[1]
    #                 qty_product = product_on_id.split('+')[0]
    #                 # print " CODIGO DEL VENDEDOR",sale_tpv_cod
    #                 product_id = product_obj.search(cr, uid, ['|',('default_code','=',cod_product),('ean13','=',cod_product)])
    #                 product_br = product_obj.browse(cr, uid, product_id, context=None)[0]
    #                 for tx in product_br.taxes_id:
    #                     if tx.company_id.id == company_id:
    #                         tax_id.append(tx.id)
    #                 if product_br.default_code:
    #                     product_name = '['+product_br.default_code +']'+product_br.name
    #                 else:
    #                     product_name = product_br.name

    #                 if product_id:
    #                     xline = (0,0,{
    #                             'product_id': product_id[0],
    #                             'name': product_name,
    #                             'tax_id': [(6, 0, tax_id)],
    #                             'product_uom_qty': int(qty_product),
    #                             'price_unit': product_br.list_price,
    #                             'product_uom': product_br.uom_id.id,
    #                         })
    #                     lines.append(xline)
    #                 else:
    #                     warning = {
    #                                 'title': 'Error Captura!',
    #                                 'message': 'El Codigo Capturado no Encontro Ningun Producto en la Base de Datos, Codigo %s' % (cod_product,),
    #                             }
    #                     return {'value' : {'product_on_id':False,},'warning':warning}
    #             except:
    #                 warning = {
    #                         'title':'Error !',
    #                         'message':'La Informacion Introducida Contiene Errores Verificar que el orden de la informacion sea de los ejemplos:\
    #                          \n -[Cantidad+CodigoProducto]'}
    #                 return {'value' : {'product_on_id':False,},'warning':warning}
    #         else:
    #             try:
    #                 cod_product = product_on_id
    #                 qty_product = 1
    #                 # print " CODIGO DEL VENDEDOR",sale_tpv_cod
    #                 product_id = product_obj.search(cr, uid, ['|',('default_code','=',cod_product),('ean13','=',cod_product)])
    #                 product_br = product_obj.browse(cr, uid, product_id, context=None)[0]
    #                 if product_br.default_code:
    #                     product_name = '['+product_br.default_code +']'+product_br.name
    #                 else:
    #                     product_name = product_br.name

    #                 for tx in product_br.taxes_id:
    #                     if tx.company_id.id == company_id:
    #                         tax_id.append(tx.id)
    #                 if product_id:
    #                     xline = (0,0,{
    #                             'product_id': product_id[0],
    #                             'name': product_name,
    #                             'tax_id': [(6, 0, tax_id)],
    #                             'product_uom_qty': int(qty_product),
    #                             'price_unit': product_br.list_price,
    #                             'product_uom': product_br.uom_id.id,
    #                         })
    #                     lines.append(xline)
    #                 else:
    #                     warning = {
    #                                 'title': 'Error Captura!',
    #                                 'message': 'El Codigo Capturado no Encontro Ningun Producto en la Base de Datos, Codigo %s' % (cod_product,),
    #                             }
    #                     return {'value' : {'product_on_id':False,},'warning':warning}
    #             except:
    #                 warning = {
    #                         'title':'Error !',
    #                         'message':'La Informacion Introducida Contiene Errores Verificar que el orden de la informacion sea de los ejemplos:\
    #                          \n -[Cantidad+CodigoProducto]'}
    #                 return {'value' : {'product_on_id':False,},'warning':warning}

          
    #     return {'value' : {'product_on_id':False,'order_line':[x for x in lines]}}

    # @api.onchange('partner_id', 'product_on_id', 'product_qty', 'order_line')
    # def on_change_load_products(self):

    #     product_obj = self.env['product.product']
    #     salesman_obj = self.env['res.users']
    #     partner_obj = self.env['res.partner']
    #     partner = partner_obj.browse(self.partner_id)
    #     lines = [x.id for x in self.order_line]
    #     if not self.product_on_id:
    #         return {}

    #     qty_product = self.product_qty

    #     product_id = self.product_on_id.id
    #     product_br = product_obj.browse(product_id)
    #     if product_br.default_code:
    #         product_name = '['+product_br.default_code +']'+product_br.name
    #     else:
    #         product_name = product_br.name
    #     if product_br.property_account_income_id:
    #         account_id = product_br.property_account_income_id.id
    #     else:
    #         account_id = product_br.categ_id.property_account_income_categ_id.id
    #     price = product_br.lst_price
    #     taxes_list = [_w.id for _w in product_br.taxes_id]

    #     if product_id:
    #         xline = (0,0,{
    #                 'product_id': product_id,
    #                 'name': product_name,
    #                 'tax_id': [(6, 0, taxes_list )],
    #                 'product_uom_qty': int(qty_product),
    #                 'price_unit': price,
    #                 'product_uom': product_br.uom_id.id,
    #                 # 'account_id': account_id,
    #             })
    #         lines.append(xline)

    #     self.update({'order_line': lines})
            
    #     self.product_on_id = False
    #     self.product_qty = 1

    # @api.multi
    # def recalculate_prices(self):
    #     for record in self:
    #         if record.order_line:
    #             for line in record.order_line:
    #                 res = line.product_id_change()
    #                 #print "######### RES >>> ",res
    #                 #self.update(res)
    #     return True
