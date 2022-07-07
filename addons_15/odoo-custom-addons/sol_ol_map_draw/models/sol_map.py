# -*- coding: utf-8 -*-
#################################################################################
#
#
#################################################################################

from odoo import fields, models, _


class SolMapManageOverlay(models.Model):
    _name = 'sol.map.manage.overlay'
    _description = "Manage multiples overlay template according to the current " \
                   "model, to display in the map on marker click "

    name = fields.Char('Overlay name', translate=True, required=True)
    model_name = fields.Char('Model Name', translate=True, required=True)
    overlay_template = fields.Text('Overlay Template', required=True)
    is_default = fields.Boolean(string="Default", default=False, translate=True)
