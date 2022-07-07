import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        # default=lambda self: self.env.user.sucursal.id
    )

    equipment_id = fields.Many2one(
        'cost_center.equipment',
        # default=lambda self: self.env.user.equipo.id
    )

    business_id = fields.Many2one(
        'cost_center.business',
        # default=lambda self: self.env.user.area.id
    )

    area_id = fields.Many2one(
        'cost_center.area',
        # default=lambda self: self.env.user.department.id
    )

    type_of_operation_id = fields.Many2one(
        'cost_center.type_of_operation',
        # default=lambda self: self.env.user.tipo_operacion.id
    )
