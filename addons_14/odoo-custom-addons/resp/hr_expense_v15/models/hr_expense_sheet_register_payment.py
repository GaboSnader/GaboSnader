# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError



class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = "hr.expense.sheet.register.payment.wizard"

    forma_pago = fields.Many2one(
        'factura.forma_pago',
        string='Forma de Pago',
        required=True,
    )

    def _get_payment_vals(self):
        res = super()._get_payment_vals()
        res.update({'forma_pago': self.forma_pago.id})
        return res