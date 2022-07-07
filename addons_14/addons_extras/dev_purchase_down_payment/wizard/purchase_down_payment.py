# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class PurchaseDownPayment(models.TransientModel):
    _name = 'purchase.down.payment'

    def create_bill(self):
        self.purchase_id.down_payment_by = self.down_payment_by
        self.purchase_id.amount = self.amount

        if self.purchase_id.down_payment_by in ['fixed', 'percentage']:
            if self.amount <= 0:
                raise ValidationError(_('''Amount must be positive'''))
            if self.purchase_id.down_payment_by == 'percentage':
                payment = self.purchase_id.amount_total * self.purchase_id.amount / 100
            else:
                payment = self.amount

            if self.purchase_id.total_invoices_amount == 0:
                if payment > self.purchase_id.amount_total:
                    raise ValidationError(_('''You are trying to pay: %s, but\n You can not pay more than: %s''') % (payment, self.purchase_id.amount_total))
            if self.purchase_id.total_invoices_amount == self.purchase_id.amount_total:
                raise ValidationError(_('''Bills worth %s already created for this purchase order, check attached bills''') % (self.purchase_id.amount_total))
            if self.purchase_id.total_invoices_amount > 0:
                remaining_amount = self.purchase_id.amount_total - self.purchase_id.total_invoices_amount
                if payment > remaining_amount:
                    raise ValidationError(_('''You are trying to pay: %s, but\n You have already paid: %s for purchase order worth: %s''') % (payment, self.purchase_id.total_invoices_amount, self.purchase_id.amount_total))
            if payment > self.purchase_id.amount_total:
                raise ValidationError(_('''You are trying to pay: %s, but\n You can not pay more than: %s''') % (payment, self.purchase_id.amount_total))

        product = self.purchase_id.company_id.down_payment_product_id
        journal_id = self.env['account.journal'].search([('type', '=', 'purchase'), ('company_id', '=', self.purchase_id.company_id.id)], limit=1)
        if journal_id:
            self.purchase_id.dp_journal_id = journal_id.id
        else:
            raise ValidationError(_('''Please configure at least one Purchase Journal for %s Company''') % (self.purchase_id.company_id.name))

        if not product:
            raise ValidationError(_('''Please configure Advance Payment Product into : Purchase > Settings'''))

        # choose the view_mode accordingly
        action = self.env.ref('account.action_move_in_invoice_type').sudo()
        result = action.read()[0]
        res = self.env.ref('account.view_move_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in result:
            result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            result['views'] = form_view
        result['context'] = {'default_type': 'in_invoice',
                             'default_company_id': self.purchase_id.company_id.id,
                             'default_purchase_id': self.purchase_id.id,
                             'default_origin': self.purchase_id.name,
                             'default_reference': self.purchase_id.partner_ref,
                             'default_move_type': 'in_invoice'
                             }
        # action = self.env.ref('account.action_move_in_invoice_type').sudo()
        # result = action.read()[0]
        # # choose the view_mode accordingly
        # if len(self.purchase_id.invoice_ids) > 1:
        #     result['domain'] = [('id', 'in', self.purchase_id.invoice_ids.ids)]
        # elif len(self.purchase_id.invoice_ids) == 1:
        #     res = self.env.ref('account.view_move_form', False)
        #     form_view = [(res and res.id or False, 'form')]
        #     if 'views' in result:
        #         result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        #     else:
        #         result['views'] = form_view
        #     result['res_id'] = self.purchase_id.invoice_ids[0].id
        # result['context'] = {'default_type': 'in_invoice',
        #                      'default_company_id': self.purchase_id.company_id.id,
        #                      'default_purchase_id': self.purchase_id.id,
        #                      'default_origin': self.purchase_id.name,
        #                      'default_reference': self.purchase_id.partner_ref,
        #                      'default_move_type': 'in_invoice'
        #                      }
        return result

    down_payment_by = fields.Selection(selection=[('dont_deduct_down_payment', 'Billable lines'),
                                                  ('deduct_down_payment', 'Billable lines (deduct advance payments)'),
                                                  ('percentage', 'Advance payment (percentage)'),
                                                  ('fixed', 'Advance payment (fixed amount)')],
                                       string='What do you want to bill?', default='fixed')
    amount = fields.Float(string='Amount')
    purchase_id = fields.Many2one('purchase.order', string='Purchase')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: