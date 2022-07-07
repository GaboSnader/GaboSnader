from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare, float_round

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from itertools import groupby
from pytz import timezone, UTC
from werkzeug.urls import url_encode

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_code = fields.Char(compute="_compute_extra_codes", store=True)
    customer_code = fields.Char(compute="_compute_extra_codes", store=True)

    @api.multi
    @api.depends('create_uid')
    def _compute_extra_codes(self):
        for partner in self:
            code = str(partner.id).zfill(8)
            partner.supplier_code = "P" + code
            partner.customer_code = "C" + code
