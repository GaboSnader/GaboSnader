from odoo import models, fields


class Business(models.Model):
    _name = 'cost_center.business'
    _description = "Business"
    _check_company_auto = True

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company
    )

    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        'cost_center_business_warehouse_rel',
        'business_id',
        'warehouse_id',
        check_company=True
    )

    _sql_constraints = [
        ('business_code_uniq',
         'UNIQUE(code)',
         'Code must be unique.')
    ]
