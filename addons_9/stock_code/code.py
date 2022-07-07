# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, UserError

class stock_move_code(models.TransientModel):
    _name = 'stock.move.code'

    product_on_read = fields.Char('Lectura Codigo de Barras')
    location_id = fields.Many2one('stock.location', 'Ubicacion Origen', required=True)
    location_dest_id = fields.Many2one('stock.location', 'Ubicacion Destino', required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Tipo de Albaran', required=True, filter=('internal'))

    code_lines = fields.One2many('stock.code', 'code_id', string="Lineas de Productos")

    @api.onchange('picking_type_id')
    def onchange_picking(self):
        for pick in self.picking_type_id:
            self.location_id = pick.default_location_src_id.id
            self.location_dest_id = pick.default_location_dest_id.id

    @api.onchange('product_on_read')
    def onchange_on_read(self):
        if self.product_on_read:
            product_split = self.product_on_read.split("+")
            product_code = product_split[0]
            qty = 1
            if '+' in self.product_on_read:
                qty = product_split[1]
            default_code = product_code
            product_obj = self.env['product.product']
            product_id = product_obj.search([('barcode','=',default_code)])
            if product_id:
                xline = {
                        'product_id': product_id.id,
                        'name': product_id.name,
                        'qty': qty,
                        'product_uom_id': product_id.uom_id.id,
                    }
            else:
                raise UserError(_("Error!\nEl codigo [%s] no coincide con ninguna referencia de Producto." % default_code))
            self.code_lines += self.code_lines.new(xline)
            self.product_on_read = False

    @api.multi
    def generate_stock(self):
        print "####### GENERATE STOCK >>>>> "
        picking_obj = self.env['stock.picking']
        picking_lines = {
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.location_id.company_id.id,
            'move_type': 'direct',
            'priority': '1',
            }
        picking_id = picking_obj.create(picking_lines)
        print "###### id >>>>>>> ", picking_id
        stock_move_obj = self.env['stock.move']
        for line in self.code_lines:
            print "####### LINES QTY >>>>>>>>> ", line.qty
            stock_move_vals = {
                'picking_id': picking_id.id,
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.qty,
                'product_uom': line.product_id.uom_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'state': 'draft',
                'procure_method': 'make_to_stock',
                'company_id': self.location_id.company_id.id,
                'picking_type_id': self.picking_type_id.id,
                'scrapped': False,
            }
            move_id = stock_move_obj.create(stock_move_vals)
        print "###### MOVE ID >>>>>>>>> ", move_id
        return {
                'name': _('Transfer'),
                'view_mode': 'form',
                'view_id': self.env.ref('stock.view_picking_form').id,
                'res_model': 'stock.picking',
                'context': "{}", # self.env.context
                'type': 'ir.actions.act_window',
                'res_id': picking_id.id,
                }

class stock_code(models.TransientModel):
    _name = 'stock.code'

    product_id = fields.Many2one('product.product', 'Producto')
    name = fields.Char('Descripcion')
    qty = fields.Float('Cantidad')
    product_uom_id = fields.Many2one('product.uom', 'Unidad de Medida')
    code_id = fields.Many2one('stock.move.code', 'Reference Code', readonly=True)

#class stock_picking(models.Model):
    #_inherit = 'stock.picking'

    #product_on_read = fields.Char('Lectura Codigo de Barras')

    #code_lines = fields.One2many('stock.code', 'code_id', string="Lineas de Productos")

    #@api.onchange('picking_type_id')
    #def onchange_picking(self):
    #    for pick in self.picking_type_id:
    #        self.location_id = pick.default_location_src_id
    #        self.location_dest_id = pick.default_location_dest_id

    #@api.onchange('location_id', 'location_dest_id', 'min_date', 'picking_type_id')
    #def onchange_location(self):
    #    for move in self.move_lines:
    #        move.location_id = self.location_id
    #        move.location_dest_id = self.location_dest_id
    #        move.date_expected = self.min_date
    #        move.date = self.min_date
    #        move.name = move.product_id.name
    #        print "####### SELF PPICKING TYPE >>>>> ", self.picking_type_id.id
    #        move.picking_type_id = self.picking_type_id.id
    #        print "######## SELF ONCHANGE PICKING TYPE >>>>> ", move.picking_type_id
    #        print "######## MOVE NAME >>>>>>>>> ", move.name

