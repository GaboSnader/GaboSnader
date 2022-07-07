# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TestMod(models.Model):
    _name = 'hr_expense_v15.test_mod'
    _description = 'hr_expense_v15.test_mod'
    
    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()
#
    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100