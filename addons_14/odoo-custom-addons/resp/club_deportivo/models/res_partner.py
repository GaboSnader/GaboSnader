# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning
import logging
import re

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_number = fields.Char(
        string="Número de socio",
        readonly=False,
        required=True,
        index=True,
        copy=False,
        default = lambda self: _('New'),
    )

    fecha_ingreso = fields.Date(string="fecha de Ingreso")

    @api.model
    def create(self, vals):
        if self.env.company.id == 2:
            if vals['parent_id']:
                _logger.error("***SI***"+str(vals['parent_id']))
                num = vals['parent_id']
                num2 = self.env['res.partner'].search([('id','=',num)])
                num3 = self.env['res.partner'].search([('parent_id','=',num)])
                _logger.error("***SI***"+str(num2))
                vals['partner_number'] = str(num2.partner_number) + '-' + str(len(num3)+1)
            else:
                vals['partner_number'] = self.env['ir.sequence'].next_by_code('res.partner')
        return super(ResPartner, self).create(vals)

