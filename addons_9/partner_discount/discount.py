# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, UserError

class category_discount(models.Model):
    _name = 'category.discount'

    name = fields.Char('Categoría')
    max_discount = fields.Float('Descuento Máximo (%)', digits=(2,2))
    category_discount = fields.Many2one('res.partner', 'Ref_id')

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def write(values):
        print "######## VALUES >>>>>>>> ", values
        res = super(sale_order_line, self).write(values)
        if res.order_id.skip_discount == False:
            if res.order_id.partner_id.categ_id.max_discount < res.discount:
                raise ValidationError(_('El producto %s tiene un descuento mayor al permitido'%(res.product_id.name)))
            if not self.order_id.partner_id.categ_id:
                raise ValidationError(_('El cliente %s no tiene asignada una Categoria de Descuento'%(self.order_id.partner_id.name)))
        return res

    @api.model
    def create(self, values):
        res = super(sale_order_line, self).create(values)
        if res.order_id.skip_discount == False:
            if res.order_id.partner_id.categ_id.max_discount < res.discount:
                raise ValidationError(_('El producto %s tiene un descuento mayor al permitido'%(res.product_id.name)))
            if not res.order_id.partner_id.categ_id:
                raise ValidationError(_('El cliente %s no tiene asignada una Categoria de Descuento'%(res.order_id.partner_id.name)))
        return res

class sale_order(models.Model):
    _inherit = 'sale.order'

    skip_discount = fields.Boolean('Omitir limite de descuento')

    @api.onchange('partner_id')
    def onchange_partner_categ_id(self):
        if self.skip_discount == False:
            if self.partner_id:
                if not self.partner_id.categ_id:
                    raise ValidationError(_('El cliente %s no tiene asignada una Categoria de Descuento'%(self.partner_id.name)))

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_discount_default(self):
        discount = 100
        categ_obj = self.env['category.discount'].search([('max_discount','<',discount)])
        for cat in categ_obj:
            if discount > cat.max_discount:
                discount = cat.max_discount
        categ_id = self.env['category.discount'].search([('max_discount','=',discount)])
        return categ_id

    categ_id = fields.Many2one('category.discount', 'Categoría', required=True, default=_get_discount_default)



