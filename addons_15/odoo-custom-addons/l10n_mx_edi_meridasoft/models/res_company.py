# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

class ResCompanyMS(models.Model):
    _inherit = 'res.company'

    l10n_mx_edi_pac = fields.Selection(selection_add=[('ms_pac','Méridasoft WS')])
