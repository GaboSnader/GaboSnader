# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, UserError

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    product_on_read = fields.Char('Lectura Codigo de Barras')

    @api.onchange('product_on_read')
    def onchange_product_on_read(self):
        #lines = [x.id for x in self.move_lines]
        #picking_id = self._origin.id
        #print "######### self._origin.id ", picking_id
        if self.product_on_read:
            lines = [x.id for x in self.move_lines]
            product_split = self.product_on_read.split("+")
            product_code = product_split[0]
            qty = 1
            if '+' in self.product_on_read:
                qty = product_split[1]
            default_code = product_code


            if len(default_code) > 12:
                default_code = default_code[0:12]
            self.env.cr.execute("""
                select id from product_product where UPPER(default_code) = %s;
                """, (default_code.upper(),))
            cr_res = self.env.cr.fetchall()
            product_search = [x[0] for x in cr_res]
            if not product_search:
                self.env.cr.execute("""
                    select id from product_product where UPPER(barcode) like %s;
                    """, ('%'+default_code.upper()+'%',))
                cr_res = self.env.cr.fetchall()
                product_search = [x[0] for x in cr_res]
                if not product_search:
                    raise UserError(_("Error!\nEl codigo [%s] no coincide con ninguna referencia de Producto." % default_code))


            product_id = product_search[0]
            product_obj = self.env['product.product']
            product_ref = product_obj.browse(product_id)
            print "####### SELF PICKING TYPE ID >>>>>>> ", self.picking_type_id
            if product_id:
                xline = {
                    'product_id': product_id,
                    'name': product_ref.name,
                    'product_uom_qty': qty,
                    'product_uom': product_ref.uom_id.id,
                    'date': self.min_date,
                    #'date_expected': self.min_date,
                    'location_id': self.location_id,
                    'location_dest_id': self.location_dest_id.id,
                    'state': 'draft',
                    #'procure_method': 'make_to_stock',
                    'company_id': self.location_id.company_id.id,
                    'picking_type_id': self.picking_type_id.id,
                    # 'scrapped': False,
                    }
                #lines.append(self.env['stock.move'].new(xline))
            self.move_lines += self.move_lines.new(xline)
            #self.move_lines_related += self.move_lines_related.new(xline)
            #self.product_on_read = False

    @api.model
    def create(self, values):
        print "########## VALUES >>>> ",values
        res = super(stock_picking,self).create(values)
        qty = 1
        print "########### PRODUCT ON READ >>>>>>>> ", res.product_on_read
        if self.product_on_read:
            product_split = self.product_on_read.split("+")
            product_code = product_split[0]
            qty = 1
            if '+' in self.product_on_read:
                qty = product_split[1]
            default_code = product_code


            if len(default_code) > 12:
                default_code = default_code[0:12]
            self.env.cr.execute("""
                select id from product_product where UPPER(default_code) = %s;
                """, (default_code.upper(),))
            cr_res = self.env.cr.fetchall()
            product_search = [x[0] for x in cr_res]
            if not product_search:
                self.env.cr.execute("""
                    select id from product_product where UPPER(barcode) like %s;
                    """, ('%'+default_code.upper()+'%',))
                cr_res = self.env.cr.fetchall()
                product_search = [x[0] for x in cr_res]
                if not product_search:
                    raise UserError(_("Error!\nEl codigo [%s] no coincide con ninguna referencia de Producto." % default_code))

            product_id = product_search[0]
            product_obj = self.env['product.product']
            product_ref = product_obj.browse(product_id)
            values.update({
                'product_id': product_id,
                'name': product_ref.name,
                'product_uom_qty': qty,
                'product_uom': product_ref.uom_id.id,
                'date': res.min_date,
                'date_expected': res.min_date,
                'location_id': res.location_id.id,
                'location_dest_id': res.location_dest_id.id,
                'state': 'draft',
                'procure_method': 'make_to_stock',
                'company_id': res.location_id.company_id.id,
                #'picking_type_id': res.picking_type_id.id,
                #'scrapped': False,
                })
            res.product_on_read = False
            print "########## PRODUCT_REGISTRADO >>>>>>>>> ", res.product_on_read
            self.create(values)
        return res


    #    if self.product_on_read != False:
    #        product_obj = self.env['product.product']
    #        product_id = partner_obj.search([('barcode','=',pick.product_on_read)])
    #        print '################## SELF PRODUCT ID >>>>>>>>>>>>>>>>>>>>>> ', product_id
    #        if product_id:
    #            values.update({
    #                            'product_id': product_id,
    #                            'product_uom_qty': 1.000
    #                            })
    #            self.create(values)
    #        else:
    #            raise ValidationError(_('Error!\nNo se ha encontrado el codigo'))
    #    self.product_on_read = False
    #    return True