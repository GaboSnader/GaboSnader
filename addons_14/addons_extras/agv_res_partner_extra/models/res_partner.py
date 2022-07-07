from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_code = fields.Char(compute="_compute_extra_codes", store=True)
    customer_code = fields.Char(compute="_compute_extra_codes", store=True)
    id_radical = fields.Integer()
    id_openbravo = fields.Char()

    _sql_constraints = [
        ('id_radical_unique',
         'UNIQUE(id_radical)',
         'Id Radical is already assigned.'),
        ('id_openbravo_unique',
         'UNIQUE(id_openbravo)',
         'Id Openbravo is already assigned.'),
    ]

    @api.depends('create_uid')
    def _compute_extra_codes(self):
        for partner in self:
            code = str(partner.id).zfill(8)
            partner.supplier_code = "P" + code
            partner.customer_code = "C" + code
