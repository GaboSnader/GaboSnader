from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    cost_center_area_ids = fields.Many2many(
        'cost_center.area',
        'cost_center_area_department_rel',
        'department_id',
        'area_id',
        check_company=True
    )
