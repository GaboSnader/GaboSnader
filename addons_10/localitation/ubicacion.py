# -*- coding: utf-8 -*-
#!/usr/bin/python
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class location_alt(models.Model):
    _name = 'location.alt'
    loc_alt = fields.Many2one('stock.warehouse', 'Almacenamiento Alterna')