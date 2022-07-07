from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    preference_department_id = fields.Many2one(
        'hr.department',
        company_dependent=True,
        check_company=True,
        domain="[('cost_center_area_ids', 'in', area_id)]"
    )
    area_id = fields.Many2one(
        'cost_center.area',
        company_dependent=True,
        check_company=True,
        domain="[('warehouse_ids', 'in', property_warehouse_id)]"
    )
    equipment_id = fields.Many2one(
        'cost_center.equipment',
        company_dependent=True,
        check_company=True,
        domain="[('warehouse_ids', 'in', property_warehouse_id)]"
    )
    type_of_operation_id = fields.Many2one(
        'cost_center.type_of_operation',
        company_dependent=True,
        check_company=True,
        domain="[('warehouse_ids', 'in', property_warehouse_id)]"
    )
    business_id = fields.Many2one(
        'cost_center.business',
        company_dependent=True,
        check_company=True,
        domain="[('warehouse_ids', 'in', property_warehouse_id)]"
    )

    @api.onchange('area_id')
    def _onchange_area_id(self):
        if self.area_id not in self.preference_department_id.cost_center_area_ids:
            self.preference_department_id = None

    @api.onchange('property_warehouse_id')
    def _onchange_warehouse_id(self):
        if self.property_warehouse_id not in self.area_id.warehouse_ids:
            self.area_id = None
        if self.property_warehouse_id not in self.equipment_id.warehouse_ids:
            self.equipment_id = None
        if self.property_warehouse_id not in self.type_of_operation_id.warehouse_ids:
            self.type_of_operation_id = None
        if self.property_warehouse_id not in self.business_id.warehouse_ids:
            self.business_id = None
