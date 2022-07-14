# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields, _

_logger = logging.getLogger(__name__)


class SaleReport(models.Model):
    _inherit = 'sale.report'

    @api.depends('warehouse_id')
    def _get_location_products(self):
        for rec in self:
            rec.ensure_one()
            if self.warehouse_id.lot_stock_id.branch == 'MAN':
                self.suc_manantial = 1
            else:
                self.suc_manantial = False
            if self.warehouse_id.lot_stock_id.branch == 'MAG':
                self.suc_magon = 1
            else:
                self.suc_magon = 0
            if self.warehouse_id.lot_stock_id.branch == 'POZ':
                self.suc_poza_rica = 1
            else:
                self.suc_poza_rica = 0
            if self.warehouse_id.lot_stock_id.branch == 'PAP':
                self.suc_papantla = 1
            else:
                self.suc_papantla = 0
            if self.warehouse_id.lot_stock_id.branch == 'TUX':
                self.suc_tuxpan = 1
            else:
                self.suc_tuxpan = 0

    
    suc_manantial = fields.Boolean(string="Suc. Manantial") #, compute=_get_location_products, default=0)
    suc_magon = fields.Boolean(string="Suc. Magon") #, compute=_get_location_products, default=0)
    suc_poza_rica = fields.Boolean(string="Suc. Poza Rica",) # compute=_get_location_products, default=0)
    suc_papantla = fields.Boolean(string="Suc. Papantla") #, compute=_get_location_products, default=0)
    suc_tuxpan = fields.Boolean(string="Suc. Tuxpan") #, compute=_get_location_products, default=0)

    # def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
    #     print("################# FIELDS >>>>>>>>>>>>>>>>>>>>>>> ", fields)
    #     fields['suc_manantial'] = ", s.suc_manantial as suc_manantial"
    #     # groupby += ", "+str(self.suc_manantial)
    #     res = super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
    #     # self.suc_manantial = 1.0
    #     return res
