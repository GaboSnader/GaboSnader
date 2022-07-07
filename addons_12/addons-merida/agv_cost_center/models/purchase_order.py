import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        related='picking_type_id.warehouse_id',
        readonly=True,
    )

    preference_department_id = fields.Many2one(
        'hr.department',
        check_company=True,
        domain="[('cost_center_area_ids', 'in', area_id)]",
        default=lambda self: self.env.user.preference_department_id.id,
        states={
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]
        }
    )

    area_id = fields.Many2one(
        'cost_center.area',
        check_company=True,
        domain="[('warehouse_ids', 'in', warehouse_id)]",
        default=lambda self: self.env.user.area_id,
        states={
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]
        }
    )
    equipment_id = fields.Many2one(
        'cost_center.equipment',
        check_company=True,
        domain="[('warehouse_ids', 'in', warehouse_id)]",
        default=lambda self: self.env.user.equipment_id,
        states={
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]
        }
    )
    type_of_operation_id = fields.Many2one(
        'cost_center.type_of_operation',
        check_company=True,
        domain="[('warehouse_ids', 'in', warehouse_id)]",
        default=lambda self: self.env.user.type_of_operation_id.id,
        states={
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]
        }
    )
    business_id = fields.Many2one(
        'cost_center.business',
        check_company=True,
        domain="[('warehouse_ids', 'in', warehouse_id)]",
        default=lambda self: self.env.user.business_id,
        states={
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]
        }
    )

    @api.onchange('area_id')
    def _onchange_area_id(self):
        if self.area_id not in self.preference_department_id.cost_center_area_ids:
            self.preference_department_id = None

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        if self.warehouse_id not in self.area_id.warehouse_ids:
            self.area_id = None
        if self.warehouse_id not in self.equipment_id.warehouse_ids:
            self.equipment_id = None
        if self.warehouse_id not in self.type_of_operation_id.warehouse_ids:
            self.type_of_operation_id = None
        if self.warehouse_id not in self.business_id.warehouse_ids:
            self.business_id = None


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        related='order_id.warehouse_id',
        readonly=True,
    )

    preference_department_id = fields.Many2one(
        'hr.department',
        check_company=True,
        domain="[('cost_center_area_ids', 'in', area_id)]",
    )
    area_id = fields.Many2one(
        'cost_center.area',
        check_company=True,
        domain="[('warehouse_ids', 'in', warehouse_id)]",
    )
    equipment_id = fields.Many2one(
        'cost_center.equipment',
        check_company=True,
        domain="[('warehouse_ids', 'in', warehouse_id)]",
    )
    type_of_operation_id = fields.Many2one(
        'cost_center.type_of_operation',
        check_company=True,
        domain="[('warehouse_ids', 'in', warehouse_id)]",
    )
    business_id = fields.Many2one(
        'cost_center.business',
        check_company=True,
        domain="[('warehouse_ids', 'in', warehouse_id)]",
    )

    @api.onchange('area_id')
    def _onchange_area_id(self):
        if self.area_id not in self.preference_department_id.cost_center_area_ids:
            self.preference_department_id = None

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        if self.warehouse_id not in self.area_id.warehouse_ids:
            self.area_id = None
        if self.warehouse_id not in self.equipment_id.warehouse_ids:
            self.equipment_id = None
        if self.warehouse_id not in self.type_of_operation_id.warehouse_ids:
            self.type_of_operation_id = None
        if self.warehouse_id not in self.business_id.warehouse_ids:
            self.business_id = None

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.update({
            'equipment_id': self.order_id.equipment_id.id,
            'business_id': self.order_id.business_id.id,
            'area_id': self.order_id.area_id.id,
            'preference_department_id': self.order_id.preference_department_id.id,
            'type_of_operation_id': self.order_id.type_of_operation_id.id,
        })
