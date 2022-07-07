from odoo import models, fields
from odoo.exceptions import ValidationError
# clase ligada al equipo de mantenimiento maintenance.equipment ver equipment.py


class Equipment(models.Model):
    _name = 'cost_center.equipment'
    _description = "Equipment"
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
        'cost_center_equipment_warehouse_rel',
        'equipment_id',
        'warehouse_id',
        check_company=True
    )

    _sql_constraints = [
        ('equipment_code_uniq',
         'UNIQUE(code)',
         'Code must be unique.')
    ]

    # def write(self, vals):
    #     # no se debe permitir la modificación del registro con clave GEN ya que es el generico por default
    #     # en self.clave tenemos el valor anterior
    #     # en vals.get('clave') tenemos el valor actualizado
    #     # cualquier modificacion en mantenimiento se refleja en costos
    #     if str(self.clave) == 'GEN':
    #         if vals.get('clave') is not None:  # intentan cambiar la clave?
    #             if vals.get('clave') != 'GEN':
    #                 raise ValidationError(
    #                     'No se debe modificar la clave  General.')
    #         if vals.get('equipo') is not None:
    #             if vals.get('equipo') != 'General':
    #                 raise ValidationError(
    #                     'No se debe modificar el equipo  General.')
    #         if vals.get('active') is not None:
    #             if vals.get('active') != 1:
    #                 raise ValidationError(
    #                     'No se debe desactivar el equipo   General.')
    #         # if vals.get('description') is not None:
    #         #     if vals.get('description') != 'General':
    #         #         raise ValidationError('No se debe modificar la descripción del equipo de   General.')
    #     # todos los valores de vals a res
    #     res = super(Equipment, self).write(vals)
    #     return res
    # # si eliminan el equipo en mantenimiento se elimina tambien en costos

    # def unlink(self):
    #     if str(self.clave) == 'GEN':
    #         raise ValidationError('No se debe eliminar la clave General.')
    #     return super(Equipment, self).unlink()
