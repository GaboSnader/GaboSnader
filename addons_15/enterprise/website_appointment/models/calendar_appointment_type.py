# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.addons.http_routing.models.ir_http import slug


class CalendarAppointmentType(models.Model):
    _name = "calendar.appointment.type"
    _inherit = [
        'calendar.appointment.type',
        'website.seo.metadata',
        'website.published.mixin',
        'website.cover_properties.mixin',
    ]

    @api.model
    def default_get(self, default_fields):
        result = super().default_get(default_fields)
        if 'category' not in default_fields or result.get('category') in ['custom', 'work_hours']:
            result['is_published'] = True
        return result

    def _default_cover_properties(self):
        res = super()._default_cover_properties()
        res.update({
            'background-image': 'url("/website_appointment/static/src/img/appointment_cover_0.jpg")',
            'resize_class': 'o_record_has_cover o_half_screen_height',
            'opacity': '0.4',
        })
        return res

    def _compute_website_url(self):
        super(CalendarAppointmentType, self)._compute_website_url()
        for appointment_type in self:
            if appointment_type.id:
                appointment_type.website_url = '/calendar/%s/appointment' % (slug(appointment_type),)
            else:
                appointment_type.website_url = False

    def get_backend_menu_id(self):
        return self.env.ref('calendar.mail_menu_calendar').id
