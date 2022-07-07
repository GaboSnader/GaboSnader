# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class extend_prodduct_name(models.Model):
    _name = 'extend.date'
    _inherit = ''
    _description = 'Extender Fecha de Vencimiento'

    line_ids = fields.Many2many('account.move.line')
