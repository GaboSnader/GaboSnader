# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields, _

_logger = logging.getLogger(__name__)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    branch = fields.Selection(
        selection=[('MAN', 'Manantial'), 
                   ('MAG', 'Magon'),
                   ('POZ', 'Poza Rica'),
                   ('PAP', 'Papantla'),
                   ('TUX', 'Tuxpan'),],
        string=_('Sucursal'), required=True,
    )

