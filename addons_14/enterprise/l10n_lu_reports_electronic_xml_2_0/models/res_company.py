# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_lu_agent_vat = fields.Char(
        string="Agent's VAT",
        help="VAT number of the accounting firm (agent company) acting as the declarer in eCDF declarations")
    l10n_lu_agent_matr_number = fields.Char(
        string="Agent's Matr Number",
        help="National ID number of the accounting firm (agent company) acting as the declarer in eCDF declarations")
    l10n_lu_agent_ecdf_prefix = fields.Char(
        string="Agent's ECDF Prefix",
        help="eCDF prefix (identifier) of the accounting firm (agent company) acting as the declarer in eCDF declarations")
    l10n_lu_agent_rcs_number = fields.Char(
        string="Agent's Company Registry",
        help="RCS (Régistre de Commerce et des Sociétés) of the accounting firm (agent company) acting as the declarer in eCDF declarations")
