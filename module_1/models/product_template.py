# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields, _

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('qty_available')
    def _get_location_products(self):
        for rec in self:
            rec.ensure_one()
            quant_ids = self.env['stock.quant'].search([('product_id.name','=',rec.name)])
            if not quant_ids:
                rec.suc_manantial = 0
                rec.suc_magon = 0
                rec.suc_poza_rica = 0
                rec.suc_papantla = 0
                rec.suc_tuxpan = 0
            for quant in quant_ids:
                if quant.location_id.branch == 'MAN' and quant.product_id.default_code == rec.default_code:
                    rec.suc_manantial = quant.quantity
                else:
                    rec.suc_manantial = rec.suc_manantial
                if quant.location_id.branch == 'MAG' and quant.product_id.default_code == rec.default_code:
                    rec.suc_magon = quant.quantity
                else:
                    rec.suc_magon = rec.suc_magon
                if quant.location_id.branch == 'POZ' and quant.product_id.default_code == rec.default_code:
                    rec.suc_poza_rica = quant.quantity
                else:
                    rec.suc_poza_rica = rec.suc_poza_rica
                if quant.location_id.branch == 'PAP' and quant.product_id.default_code == rec.default_code:
                    print("#################### QUANt >>>>>>>>>>>>>>>>>>>>> ", quant)
                    rec.suc_papantla = quant.quantity
                else:
                    rec.suc_papantla = rec.suc_papantla
                if quant.location_id.branch == 'TUX' and quant.product_id.default_code == rec.default_code:
                    rec.suc_tuxpan = quant.quantity
                else:
                    rec.suc_tuxpan = rec.suc_tuxpan

    suc_manantial = fields.Float(string="Suc. Manantial", compute=_get_location_products, default=0)
    suc_magon = fields.Float(string="Suc. Magon", compute=_get_location_products, default=0)
    suc_poza_rica = fields.Float(string="Suc. Poza Rica", compute=_get_location_products, default=0)
    suc_papantla = fields.Float(string="Suc. Papantla", compute=_get_location_products, default=0)
    suc_tuxpan = fields.Float(string="Suc. Tuxpan", compute=_get_location_products, default=0)

# class StockQuant(models.Model):
#     _inherit = 'stock.quant'

#     def write(self, vals):
#         res = super(StockQuant, self).write(vals)
#         if 'quantity' in vals:
#             for product in self.product_id:
#                 if self.location_id.branch == 'MAN':
#                     print("################# MAN >>>>>>>>>>>>>>>>>>>>>< ", vals['quantity'])
#                     product.suc_manantial += vals['quantity']
#                 else:
#                     product.suc_manantial = product.suc_manantial
#                 if self.location_id.branch == 'MAG':
#                     product.suc_magon += vals['quantity']
#                 else:
#                     product.suc_magon = product.suc_magon
#                 if self.location_id.branch == 'POZ':
#                     print("################# POZ >>>>>>>>>>>>>>>>>>>>>< ", vals['quantity'])
#                     product.suc_poza_rica += vals['quantity']
#                 else:
#                     product.suc_poza_rica = product.suc_poza_rica
#                 if self.location_id.branch == 'PAP':
#                     product.suc_papantla += vals['quantity']
#                 else:
#                     product.suc_papantla = product.suc_papantla
#                 if self.location_id.branch == 'TUX':
#                     product.suc_tuxpan += vals['quantity']
#                 else:
#                     product.suc_tuxpan = product.suc_tuxpan
#         return res

