# -*- coding: utf-8 -*-

from odoo import api, fields, models


class DocumentosExpediente(models.Model):
    _name = 'custom_contacts.documentos_expediente'

    owner_id = fields.Many2one('res.partner', string="Propietario")
    sale_id = fields.Many2one('sale.order', string="Ventas")
    partner_id = fields.Many2one('res.partner', string="Cliente")
    state = fields.Selection([
        ('draft','Borrador'),
        ('progress','En progreso'),
        ('done','Confirmado'),
    ], string="Estatus", default="draft")

    def get_contracts(self):
        return {
            'name'          :   'Generar Contrato',
            'type'          :   'ir.actions.act_window',
            'view_type'     :   'form',
            'view_mode'     :   'form',
            'target'        :   'new',
            'context'       :   {'default_partner_id': self.partner_id.id, 'default_owner_id': self.owner_id.id},
            'res_model'     :   'custom_contacts.get_contracts',
        }

    def name_get(self):
        res = []
        for expediente in self:
            name = (expediente.owner_id.display_name + " - " + expediente.partner_id.display_name)
            res.append((expediente.id, name))
        return res
