# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

    
class purchase_order(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('tri_approve', 'Triple Validacion'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    @api.multi
    def button_validation(self):
        #user_br = self.env['res.users'].browse([self._uid])
        self.write({'state': 'purchase'})
        self._create_picking()
        if self.company_id.po_lock == 'lock':
            self.write({'state': 'done'})
        return True

    @api.multi
    def button_approve(self, force=False):
        for order in self:
            if order.company_id.po_double_validation == 'tree_step' and order.amount_total >= order.company_id.po_triple_validation_amount:
                order.write({'state': 'tri_approve'})
            else:
                self.write({'state': 'purchase'})
                self._create_picking()
                if self.company_id.po_lock == 'lock':
                    self.write({'state': 'done'})
        return {}

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            if order.company_id.po_double_validation == 'tree_step':
                if order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id):
                    order.button_approve()
                if order.amount_total >= self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id):
                    order.write({'state': 'to approve'})
            else:
                order.write({'state': 'to approve'})
        return True

class res_company(models.Model):
    _inherit = 'res.company'

    po_double_validation = fields.Selection([
        ('one_step', 'Confirm purchase orders in one step'),
        ('two_step', 'Get 2 levels of approvals to confirm a purchase order'),
        ('tree_step', 'Requerir tres niveles de aprobación para confirmar un pedido de compra')
        ], string="Levels of Approvals", default='one_step',
        help="Provide a double validation mechanism for purchases")
    
    po_triple_validation_amount = fields.Monetary(string='Cantidad triple de validacion', default=10000,\
        help="Cantidad minima para la que se requiere triple validacion")

class purchase_config_settings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    po_triple_validation_amount = fields.Monetary(related='company_id.po_triple_validation_amount', string="Importe triple de validacion", currency_field='company_currency_id')