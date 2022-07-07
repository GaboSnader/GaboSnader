# -*- coding:utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrExpenseTravel(models.Model):

    _name = 'ms.hr.expense.travel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'MS Travels'

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code(
            'ms.hr.expense.travel') or '/'
        if 'description' in vals:
            vals['name'] = str(seq)
        return super(HrExpenseTravel, self).create(vals)

    name = fields.Char(string='Folio del documento', default='/')
    description = fields.Char('Descripción', required=False,
                              readonly=True,
                              states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Borrador'), ('confirm', 'En proceso'),
                              ('done', 'Finalizado'),
                              ('cancelled', 'Cancelado')],
                             default='draft', string='Estado')
    location_origin = fields.Char(string='Lugar de origen',
                                  readonly=True,
                                  states={'draft': [('readonly', False)]})
    city_origin = fields.Char(string='Ciudad', readonly=True, states={'draft': [('readonly', False)]})
    state_origin_id = fields.Many2one('res.country.state', string='Estado', readonly=True, states={'draft': [('readonly', False)]})
    country_origin_id = fields.Many2one('res.country', string='País', readonly=True, states={'draft': [('readonly', False)]})
    location_dest = fields.Char(string='Lugar destino',
                                readonly=True,
                                states={'draft': [('readonly', False)]})
    city_dest = fields.Char(string='Ciudad', readonly=True, states={'draft': [('readonly', False)]})
    state_dest_id = fields.Many2one('res.country.state', string='Estado', readonly=True, states={'draft': [('readonly', False)]})
    country_dest_id = fields.Many2one('res.country', string='País', readonly=True, states={'draft': [('readonly', False)]})
    date_start = fields.Date(string='Fecha de inicio', required=True,
                             readonly=True,
                             states={'draft': [('readonly', False)]})
    date_end = fields.Date(string='Fecha fin', required=True,
                           readonly=True,
                           states={'draft': [('readonly', False)]})
    date_due = fields.Date('Fecha limite de comprobación', readonly=True,
                           states={'draft': [('readonly', False)],
                                   'request': [('readonly', False)]})
    tipo_comision = fields.Selection([('nac', 'Nacional'), ('inter', 'Internacional')], default='nac',
                                     string=u'Tipo de comisión', readonly=True, states={'draft': [('readonly', False)]})
    attachment_number = fields.Integer('Numero de Adjuntos', compute='_compute_attachment_number')

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'ms.hr.expense.travel'),
                                                                ('res_id', 'in', self.ids)],
                                                               ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'ms.hr.expense.travel'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'ms.hr.expense.travel', 'default_res_id': self.id}
        return res

    @api.constrains('date_end', 'date_start')
    def rangedate_constrains(self):
        for record in self:
            if record.date_end < record.date_start:
                raise ValidationError(_('Lo sentimos, La fecha fin debe ser mayor o igual a la fecha de inicio!'))

    @api.constrains('date_end', 'date_due')
    def date_due_constrains(self):
        for record in self:
            if record.date_due and record.date_due <= record.date_end:
                raise ValidationError(_('Lo sentimos, La fecha límite de comprobación debe ser mayor a la fecha fin del viaje!'))


    @api.model
    def _do_date_end(self):
        ''' This method is called from a cron job.
            It is used to write end the travel.
        '''
        records = self.search([
            ('state', '=', 'confirm'),
            ('date_end', '<=', fields.Date.today()),
        ])
        _logger.debug("records cronjob => %r" % records)
        records.write({'state': 'done'})

    def button_confirm(self):
        self.state = 'confirm'

    def button_done(self):
        self.state = 'done'

    def button_cancel(self):
        self.state = 'cancelled'

    @api.onchange('country_origin_id')
    def _onchange_country_origin_id(self):
        return self._onchange_country(self.country_origin_id, 'state_origin_id')

    @api.onchange('country_dest_id')
    def _onchange_country_dest_id(self):
        return self._onchange_country(self.country_dest_id, 'state_dest_id')

    def _onchange_country(self, property, domain_property):
        res = {'domain': {domain_property: []}}
        if property:
            res['domain'][domain_property] = [('country_id', '=', property.id)]
        return res



class HrExpenseTableCategories(models.Model):
    _name = 'hr.expense.table.categories'

    _rec_name = 'categ_id'

    categ_id  = fields.Many2one(comodel_name='hr.employee.category',
                                string='Categoría')
    amount = fields.Float('Cuota diaria permitida')