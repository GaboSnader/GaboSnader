# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    campo_prueba = fields.Char('Campo Prueba')

    