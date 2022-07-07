from odoo import models, fields
from odoo.exceptions import ValidationError


class TypeOfOperation(models.Model):
    _name = 'cost_center.type_of_operation'
    _description = "Tipo de Operación"
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
        'cost_center_type_operation_warehouse_rel',
        'type_operation_id',
        'warehouse_id',
        check_company=True
    )

    _sql_constraints = [
        ('type_of_operation_code_uniq',
         'UNIQUE(code)',
         'Code must be unique.')
    ]

    # def write(self, vals):
    #     # no se debe permitir la modificación del registro con code GEN ya que es el generico por default
    #     # en self.code tenemos el valor anterior
    #     # en vals.get('code') tenemos el valor actualizado
    #     if str(self.code) == 'GEN':

    #         if vals.get('code') is not None:  # intentan cambiar la code?
    #             if vals.get('code') != 'GEN':
    #                 raise ValidationError(
    #                     'No se debe modificar la code  General.')
    #         if vals.get('tipo_operacion') is not None:
    #             if vals.get('tipo_operacion') != 'General':
    #                 raise ValidationError(
    #                     'No se debe modificar el Tipo de Operación General.')
    #         if vals.get('active') is not None:
    #             if vals.get('active') != 1:
    #                 raise ValidationError(
    #                     'No se debe desactivar el Tipo de Operación General.')
    #         if vals.get('description') is not None:
    #             if vals.get('description') != 'General':
    #                 raise ValidationError(
    #                     'No se debe modificar la descripción del Tipo de Operación General.')
    #     res = super(TipoOperacion, self).write(
    #         vals)  # todos los valores de vals a res
    #     return res

    # def unlink(self):
    #     for rec in self:
    #         if str(rec.code) == 'GEN':
    #             raise ValidationError(
    #                 'No se debe eliminar el Tipo de Operación General.')
    #     return super(TipoOperacion, self).unlink()
