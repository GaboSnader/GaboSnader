# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def preview_document_expedient(self):
        expedientes = self.env['custom_contacts.documentos_expediente'].search([('partner_id','=',self.partner_id.id)])
        for rec in self:
            for line in rec.order_line:
                propietario = line.product_id.owner_id.id
#        if len(expedientes) == 0:
        return {
            'name'          :   'Expediente',
            'type'          :   'ir.actions.act_window',
            'view_type'     :   'form',
            'view_mode'     :   'form',
            'target'        :   'current',
            'context'       :   {
                                    'default_partner_id': self.partner_id.id, 
                                    'default_owner_id': propietario,
                                    'default_sale_id': self.id
                                },
            'res_model'     :   'custom_contacts.documentos_expediente',
        }
#        else:
 #           return {
  #              'name'          :   'Expedientes',
   #             'type'          :   'ir.actions.act_window',
    #            'view_type'     :   'tree',
     #           'view_mode'     :   'tree',
      #          'target'        :   'current',
       #         'domain'        :   [('partner_id','=',self.partner_id)],
        #        'res_model'     :   'custom_contacts.documentos_expediente',
         #   }

