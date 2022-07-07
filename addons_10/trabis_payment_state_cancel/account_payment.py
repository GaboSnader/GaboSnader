# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError

#PARA FECHAS
from datetime import datetime, timedelta

##### SOLUCIONA CUALQUIER ERROR DE ENCODING (CARACTERES ESPECIALES)
import sys
reload(sys)  
sys.setdefaultencoding('utf8')


class account_payment(models.Model):
    _inherit = 'account.payment'

    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled'), ('cancel', 'Cancel')], readonly=True, default='draft', copy=False, string="Status")


    @api.multi
    def draft(self):
        for rec in self:
            # for move in rec.move_line_ids.mapped('move_id'):
            #     if rec.invoice_ids:
            #         move.line_ids.remove_move_reconcile()
            #     move.button_cancel()
            #     move.unlink()
            rec.state = 'draft'


    @api.multi
    def cancel(self):
        for rec in self:
            for move in rec.move_line_ids.mapped('move_id'):
                if rec.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                move.button_cancel()
                move.unlink()
            rec.state = 'cancel'