from odoo import models, fields, api


class Area(models.Model):
    _name = 'cost_center.area'
    _description = "Area"
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
        'cost_center_area_warehouse_rel',
        'area_id',
        'warehouse_id',
        check_company=True
    )

    hr_department_ids = fields.Many2many(
        'hr.department',
        'cost_center_area_department_rel',
        'area_id',
        'department_id',
        check_company=True
    )

    _sql_constraints = [
        ('area_code_uniq',
         'UNIQUE(code)',
         'Code must be unique.')
    ]
