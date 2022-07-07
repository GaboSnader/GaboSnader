# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
 
    @api.model
    def create(self, values):
        red_subprice = 0.0
        res = super(sale_order_line,self).create(values)
        for xpak in res.product_id.pro_ids:
            for xprc in res.order_id.pricelist_id.item_ids:
                if xprc.applied_on == '3_global':
                    if xprc.compute_price == 'fixed':
                        red_subprice = xprc.fixed_price
                    if xprc.compute_price == 'percentage':
                        red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.list_price*xprc.percent_price/100)
                    if xprc.compute_price == 'formula':
                        if xprc.base == 'list_price':
                            red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.list_price*xprc.price_discount/100)+xprc.price_surcharge+xprc.price_round+xprc.price_min_margin
                        if xprc.base == 'standard_price':
                            red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.standard_price*xprc.price_discount/100)+xprc.price_surcharge+xprc.price_round+xprc.price_min_margin
                if xprc.applied_on == '2_product_category':
                    if xpak.pack_pro_id.categ_id == xprc.categ_id:
                        if xprc.compute_price == 'fixed':
                            red_subprice = xprc.fixed_price
                        if xprc.compute_price == 'percentage':
                            red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.list_price*xprc.percent_price/100)
                        if xprc.compute_price == 'formula':
                            if xprc.base == 'list_price':
                                red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.list_price*xprc.price_discount/100)+xprc.price_surcharge+xprc.price_round+xprc.price_min_margin
                            if xprc.base == 'standard_price':
                                red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.standard_price*xprc.price_discount/100)+xprc.price_surcharge+xprc.price_round+xprc.price_min_margin
                if xprc.applied_on == '1_product':
                    if xpak.pack_pro_id.id == xprc.product_tmpl_id.id:
                        if xprc.compute_price == 'fixed':
                            red_subprice = xprc.fixed_price
                        if xprc.compute_price == 'percentage':
                            red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.list_price*xprc.percent_price/100)
                        if xprc.compute_price == 'formula':
                            if xprc.base == 'list_price':
                                red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.list_price*xprc.price_discount/100)+xprc.price_surcharge+xprc.price_round+xprc.price_min_margin
                            if xprc.base == 'standard_price':
                                red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.standard_price*xprc.price_discount/100)+xprc.price_surcharge+xprc.price_round+xprc.price_min_margin
                if xprc.applied_on == '0_product_variant':
                    if xpak.pack_pro_id.description_sale == xprc.product_id.description_sale:
                        if xprc.compute_price == 'fixed':
                            red_subprice = xprc.fixed_price
                        if xprc.compute_price == 'percentage':
                            red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.list_price*xprc.percent_price/100)
                        if xprc.compute_price == 'formula':
                            if xprc.base == 'list_price':
                                red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.list_price*xprc.price_discount/100)+xprc.price_surcharge+xprc.price_round+xprc.price_min_margin
                            if xprc.base == 'standard_price':
                                red_subprice = xpak.pack_pro_id.list_price-(xpak.pack_pro_id.standard_price*xprc.price_discount/100)+xprc.price_surcharge+xprc.price_round+xprc.price_min_margin
            if res.product_id.pack == True:
                if res.product_id.tip == False:
                        values.update({
                                        'product_id':xpak.pack_pro_id.id,
                                        'name':str(res.product_id.name)+" - "+str(xpak.pack_pro_id.name),
                                        'price_unit':0,
                                        'product_uom_qty':xpak.subtotal_price*res.product_uom_qty,
                                        })
                        self.create(values)
                if res.product_id.tip == True:
                    print "####### SELF RED SUPRICE >>>>>>> ", red_subprice
                    res.price_unit = 0.00
                    if res.order_id.pricelist_id.country_group_ids:
                        if res.order_id.pricelist_id.country_group_ids == res.order_id.partner_id.country_id:
                            values.update({
                                            'product_id':xpak.pack_pro_id.id,
                                            'name':str(res.product_id.name)+" - "+str(xpak.pack_pro_id.name),
                                            'price_unit':red_subprice,
                                            'product_uom_qty':xpak.subtotal_price*res.product_uom_qty,
                                            })
                            self.create(values)
                        else:
                            values.update({
                                            'product_id':xpak.pack_pro_id.id,
                                            'name':str(res.product_id.name)+" - "+str(xpak.pack_pro_id.name),
                                            'price_unit':xpak.pack_pro_id.list_price,
                                            'product_uom_qty':xpak.subtotal_price*res.product_uom_qty,
                                            })
                            self.create(values)
                    elif red_subprice == 0.0:
                        values.update({
                                        'product_id':xpak.pack_pro_id.id,
                                        'name':str(res.product_id.name)+" - "+str(xpak.pack_pro_id.name),
                                        'price_unit':xpak.pack_pro_id.list_price,
                                        'product_uom_qty':xpak.subtotal_price*res.product_uom_qty,
                                        })
                        self.create(values)
                    else:
                        values.update({
                                        'product_id':xpak.pack_pro_id.id,
                                        'name':str(res.product_id.name)+" - "+str(xpak.pack_pro_id.name),
                                        'price_unit':red_subprice,
                                        'product_uom_qty':xpak.subtotal_price*res.product_uom_qty,
                                        })
                        self.create(values)
        return res

class pack_product(models.Model):
    _name = 'pack.product'
    _description = 'Productos de Paquete'
      = fields.Many2one('product.template', 'Referencia')
    uni_med = fields.Many2one('product.uom', 'Unidad de medida')
    qty = fields.Float('Cantidad', digits=(3,0), default=1)
    pack_pro_id = fields.Many2one('product.template', 'Producto')
    subtotal_price = fields.Float('Qty', digits=(14,3), compute="calcula_total")
    subtotal = fields.Float('Subtotal', digits=(14,3), readonly=True)

    @api.depends('uni_med', 'qty', 'pack_pro_id')
    @api.one
    def calcula_total(self):
        if self.uni_med.uom_type == 'bigger':
            self.subtotal_price = self.uni_med.factor_inv*self.qty
            print "####### SUBTOTAL BIGGER >>>>>>>> ", self.subtotal_price
        if self.uni_med.uom_type == 'reference':
            self.subtotal_price = self.qty
            print "####### SUBTOTAL REFERENCE >>>>>>>> ", self.subtotal_price
        if self.uni_med.uom_type == 'smaller':
            self.subtotal_price = self.qty/self.uni_med.factor
            print "####### SUBTOTAL SMALLER >>>>>>>> ", self.subtotal_price

    @api.onchange('pack_pro_id', 'uni_med', 'qty')
    def calcula_subtotal(self):
        self.subtotal = self.pack_pro_id.list_price*self.subtotal_price

    @api.constrains('qty')
    @api.one
    def _check_qty(self):
        if self.qty == 0:
            raise ValidationError(_('Error en la Cantidad del Producto:\n %s \nLa Cantidad del Producto No Debe Tener Valor "0".\nSi Desea Puede Eliminar el Producto del Paquete'%self.pack_pro_id.name))

    @api.onchange('pack_pro_id')
    def onchange_uni_med(self):
        if self.pack_pro_id:
            self.uni_med = self.pack_pro_id.uom_id

    @api.constrains('pack_pro_id')
    @api.one
    def _check_pack_pro(self):
        if self.pack_pro_id.pack == True:
            raise ValidationError(_('ERROR: El Paquete No Debe Contener Productos Declarados Como Paquetes'))

class product_template(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    pack = fields.Boolean('Paquete')
    tip = fields.Boolean('Precio Basado en Componetes')
    mod_pro = fields.Boolean('Mod', default=True)

    pro_ids = fields.One2many('pack.product', 'pro_id', 'Productos')

    @api.depends('pro_ids')
    @api.one
    def calcula_product(self):
        if self.tip == True:
            acum = 0.0
            for xcal in self.pro_ids:
                acum+= xcal.pack_pro_id.list_price*xcal.subtotal_price
            if acum:
                self.pre_sale = acum
                self.list_price = 0.0

    pre_sale = fields.Float('Precio del Paquete', digits=(14,2), compute="calcula_product")

    @api.onchange('pack')
    def onchange_pack(self):
        if self.pack == False:
            prod_list = []
            self.update({'pro_ids':prod_list})

    @api.onchange('tip')
    def onchange_sale(self):
        if self.tip == True:
            acum = 0.0
            for xcal in self.pro_ids:
                acum+= xcal.pack_pro_id.list_price*xcal.subtotal_price
            if acum:
                self.pre_sale = acum
                self.list_price = 0.0

    @api.constrains('list_price')
    @api.one
    def _check_list_price(self):
        if self.pack == True:
            if self.tip == True:
                if self.list_price != 0:
                    raise ValidationError(_('El Paquete No Debe Tener Valor Si Esta Basado En Precio De Sus Componentes'))

    @api.constrains('pro_ids')
    @api.one
    def _check_categ(self):
        print "####### SELF CATEGORY >>>>>> ", self.uom_id.category_id.name
        for item in self.pro_ids:
            print "##### UNIDAD >>>>>> ", item.uni_med.name
            print "##### CATEGORIA >>>>>> ", item.uni_med.category_id.name
            if self.uom_id.category_id.name != item.uni_med.category_id.name:
                raise ValidationError(_('La Categoria de la Unidad De Medida del Producto:\n %s \nDebe ser igual a la Categoria de la Unidad del Paquete'% item.pack_pro_id.name))

    @api.constrains('pro_ids')
    @api.one
    def _check_pack(self):
        if self.pack == True:
            acum = 0.0
            for pval in self.pro_ids:
                acum+= pval.pack_pro_id.list_price
            if acum == 0.0:
                raise ValidationError(_('El Paquete Debe Contener Algun Producto'))

    _order = 'name'
    _defaults = {
        'active': True,
       }
