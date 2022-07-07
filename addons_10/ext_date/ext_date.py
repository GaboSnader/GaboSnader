# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class extend_date(models.TransientModel):
    _name = 'extend.date'
    _description = 'Extender Fecha de Vencimiento'

    line_ids = fields.Many2many('account.move.line')
    new_date = fields.Date('Nueva fecha de Vencimiento')

    @api.multi
    def new_account_date(self):
        print "############## SELF NEW DATE >>>>>>>>>>"
        for x in self.line_ids:
            x.date_maturity = self.new_date
 
