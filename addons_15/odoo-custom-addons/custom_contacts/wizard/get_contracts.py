# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models
from num2words import num2words
from lxml import etree
from dateutil.relativedelta import relativedelta
from datetime import date


_logger = logging.getLogger(__name__)

class GetContracts(models.TransientModel):
    _name = 'custom_contacts.get_contracts'

    owner_id = fields.Many2one('res.partner', string="Propietario")
    sales_ids = fields.Many2many('sale.order', string="Ventas")
    partner_id = fields.Many2one('res.partner', string="Cliente")
    contract_type = fields.Selection([
        ('compraventa','Promesa de compraventa'),
        ('rescision','Rescisión de contrato'),
        ('solicitud_res','Solicitud de rescisión'),
        ('traslativo_dom','Traslativo de dominio (Extranjeros)'),
        ('socio_const','Socio Constructor'),
    ], string="Tipo de Contracto")

    def generate_contract(self):
        if self.contract_type == 'compraventa':
            return self.env.ref('custom_contacts.custom_contacts_promesa_compraventa_report').report_action(self)
        elif self.contract_type == 'rescision':
            return self.env.ref('custom_contacts.custom_contacts_rescision_contrato_report').report_action(self)
        elif self.contract_type == 'solicitud_res':
            return self.env.ref('custom_contacts.custom_contacts_solicitud_rescision_report').report_action(self)
        elif self.contract_type == 'traslativo_dom':
            return self.env.ref('custom_contacts.custom_contacts_traslativo_dominio_report').report_action(self)
        elif self.contract_type == 'socio_const':
            return self.env.ref('custom_contacts.custom_contacts_socio_constructor_report').report_action(self)

    def _num_to_text(self, value):
        return num2words(value, lang = 'es').upper()

    def _num_to_text2(self, value):
        return num2words(value, lang = 'es').lower()


    def _get_area(self, front, depth):
        area = (float(front)*float(depth))
        return area

    def _get_restant(self, enganche, apartado): 
        total = (float(enganche)-float(apartado))
        return total

    def _get_date_apartado(self, value):
        months = {
          '01': 'enero',
          '02': 'febrero',
          '03': 'marzo',
          '04': 'abril',
          '05': 'mayo',
          '06': 'junio',
          '07': 'julio',
          '08': 'agosto',
          '09': 'septiembre',
          '10': 'octubre',
          '11': 'noviembre',
          '12': 'diciembre',

        }
        #if value = 1 gets day
        #if value = 2 gets month
        #if value = 3 gets year
        for rec in self.sales_ids:
            invoice = self.env['account.move'].search([('move_type','=','out_invoice'),('invoice_origin','=',rec.name),('journal_id.name','=','Facturas de anticipos')])
            fecha = invoice.fecha_cobro
        day = fecha.strftime("%d")
        month = fecha.strftime("%m")
        year = fecha.strftime("%Y")
        if value == 1:
            return int(day)
        elif value== 2:
            return months.get(month)
        elif value== 3:
            return int(year)

    def _get_date(self, value, field):
        months = {
          '01': 'enero',
          '02': 'febrero',
          '03': 'marzo',
          '04': 'abril',
          '05': 'mayo',
          '06': 'junio',
          '07': 'julio',
          '08': 'agosto',
          '09': 'septiembre',
          '10': 'octubre',
          '11': 'noviembre',
          '12': 'diciembre',

        }
        #if value = 1 gets day
        #if value = 2 gets month
        #if value = 3 gets year
        fecha = field
        day = fecha.strftime("%d")
        month = fecha.strftime("%m")
        year = fecha.strftime("%Y")
        if value == 1:
            return int(day)
        elif value== 2:
            return months.get(month)
        elif value== 3:
            return int(year)

    def _get_old(self, value):
        fecha = value
        today = date.today()
        difference = relativedelta(today, fecha).years
        return int(difference)

    def _get_paidnow(self):
        result = 0.0
        for rec in self.sales_ids:
            paid = self.env['account.move'].search([('move_type','=','out_invoice'),('invoice_origin','=',rec.name),('journal_id.name','in',['Facturas de cliente','Facturas de anticipos'])])
            for line in paid:
                result += line.amount_total_signed
        return result
