# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class fleet_vehicle(models.Model):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'

    tip_vehicle = fields.Selection([('plat','Plataforma de Elevacion'),
                                    ('mont','Montacargas'),
                                    ('mani','Manipuladores'),
                                    ('tor_ilum', 'Torres de Iluminacion')],'Tipo de Vehiculo')
    num_int = fields.Integer('Numero Interno')
    num_ser_equi = fields.Char('Numero Serie Equipo')
    num_fac = fields.Char('Numero de Factura')

    hor = fields.Float('Horometro')

    func = fields.Selection([('com','Combustion'),('elec','Electrico')])
    alt_t = fields.Float('Altura de Trabajo (Mts)')
    alt_p = fields.Float('Altura de Plataforma (Mts)')
    cap_car = fields.Float('Capacidad de Carga (Kg)')
    anch = fields.Float('Ancho (Mts)')
    peso = fields.Float('Peso (Ton)')
    fich_tec = fields.Text('Ficha Tecnica')

    car_max = fields.Float('Carga Maxima (Ton)')
    alt_max_mas =fields.Float('Altura Maxima de Mastil (Mts)')
    anch_equi = fields.Float('Anchura de Equipo (Mts)')
    larg_equi = fields.Float('Largo del Equipo sin Orquillas')
    alt_equi = fields.Float('Altura de Equipo (Mts)')
    larg_orq = fields.Float('Largo de Orquillas')
    rad_equi = fields.Float('Radio de Equipo')
    tip_llan = fields.Selection([('sol','Solidas'),
                                    ('sol_neu','Solidas/Neumaticas'),
                                    ('sol_no','Solidas (No Marking)')],'Tipo de Llantas')
    desp_lat = fields.Boolean('Desplazamiento Lateral')
    pes_total = fields.Float('Peso Total del Equipo')
    caract = fields.Text('Caracteristicas')

    tip = fields.Selection([('renta','Renta'),('venta','Venta'),('rent_vent','Renta/Venta')], 'Tipo')

    max_cap_alt = fields.Float('Máxima Capacidad de Carga en Altura (Ton)')
    alt_max_el = fields.Float('Altura Máxima de Elevación (Mts)')
    alt_veh = fields.Float('Altura de Vehículo (Mts)')
    long_veh = fields.Float('Longitud de Vehículo (Mts)')
    anch_veh = fields.Float('Anchura de Vehículo (Mts)')

    ilum = fields.Float('Ilumintación (Watts)')
    alt_ret = fields.Float('Alt. Mastil Retraido (mts)')
    alt_ele = fields.Float('Alt. Mastil Elevado (mts)')
    longitud = fields.Float('Longitud')
    ancho = fields.Float('Ancho')
    pes = fields.Float('Peso')

    est = fields.Many2one('fleet.vehicle')

    dia = fields.Float('Dia')
    sem = fields.Float('Semana')
    mes = fields.Float('Mes')
    mon = fields.Many2one('res.currency', 'Moneda')
    obser = fields.Text('Observaciones')
