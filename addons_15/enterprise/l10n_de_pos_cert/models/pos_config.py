# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError
import uuid


class PosConfig(models.Model):
    _inherit = 'pos.config'
    l10n_de_fiskaly_tss_id = fields.Char(string="TSS ID", readonly=True, copy=False, help="The TSS ID at Fiskaly side linked to the pos.config")
    l10n_de_fiskaly_client_id = fields.Char(string="Client ID", readonly=True, copy=False, help="The Client ID refers to the client at Fiskaly which is mapped to a pos.config")
    l10n_de_create_tss_flag = fields.Boolean(string="Create TSS", help="This allows to send a request to Fiskaly in order to create and link a TSS to the pos.config")
    is_company_country_germany = fields.Boolean(string="Company located in Germany", related='company_id.is_country_germany')

    def _l10n_de_check_fiskaly_api_key_secret(self):
        if not self.company_id.sudo().l10n_de_fiskaly_api_key or not self.company_id.sudo().l10n_de_fiskaly_api_secret:
            raise UserError(_("You have to set your Fiskaly key and secret in your company settings."))

    def _l10n_de_check_fiskaly_tss_client_ids(self):
        if not self.l10n_de_fiskaly_tss_id or not self.l10n_de_fiskaly_client_id:
            raise UserError(_("You have to set your Fiskaly TSS ID and Client ID in your PoS settings."))

    def open_ui(self):
        if not self.company_id.country_id:
            raise UserError(_("You have to set a country in your company setting."))
        if self.company_id.is_country_germany:
            self._l10n_de_check_fiskaly_api_key_secret()
            self._l10n_de_check_fiskaly_tss_client_ids()
        return super().open_ui()

    @api.model
    def l10n_de_get_fiskaly_urls_and_keys(self, config_id):
        self.check_access_rights('read')
        company = self.browse(config_id).company_id.sudo()
        return {
            'kassensichv_url': self.env['res.company']._l10n_de_fiskaly_kassensichv_url(),
            'dsfinvk_url': self.env['res.company']._l10n_de_fiskaly_dsfinvk_api_url(),
            'api_key': company.l10n_de_fiskaly_api_key,
            'api_secret': company.l10n_de_fiskaly_api_secret
        }

    @api.model
    def create(self, values):
        res = super().create(values)
        if values.get('l10n_de_create_tss_flag') is True:
            res._l10n_de_create_tss_process()
        return res

    def write(self, values):
        res = super().write(values)
        if values.get('l10n_de_create_tss_flag') is True:
            for config in self:
                config._l10n_de_create_tss_process()
        return res

    def unlink(self):
        # Those values are needed when disabling a TSS at Fiskaly, we store them before deleting the configs
        tss_to_disable = [(
            config.company_id,
            config.l10n_de_fiskaly_tss_id
        ) for config in self if config.l10n_de_create_tss_flag]
        res = super().unlink()

        # We want to first delete them in Odoo in case there's an issue and since we can't rollback with Fiskaly
        for tss in tss_to_disable:
            tss[0]._l10n_de_fiskaly_kassensichv_rpc('PUT', '/tss/%s' % tss[1], {'state': 'DISABLED'})

        return res

    def _l10n_de_create_tss_process(self):
        # If there's an unused TSS, we take it
        local_tss = {config['l10n_de_fiskaly_tss_id'] for config in self.search_read(
            [('company_id', '=', self.company_id.id), ('l10n_de_fiskaly_tss_id', '!=', False)],
            ['l10n_de_fiskaly_tss_id'])}
        fiskaly_tss = {tss['_id'] for tss in self.company_id._l10n_de_fiskaly_kassensichv_rpc('GET', '/tss').json()['data'] if tss['state'] == 'INITIALIZED'}
        free_tss = fiskaly_tss - local_tss
        if free_tss:
            tss_id = list(free_tss)[0]
        else:
            tss_id = str(uuid.uuid4())
            db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
            self.company_id._l10n_de_fiskaly_iap_rpc('/tss', {'tss_id': tss_id, 'db_uuid': db_uuid, 'tss': len(local_tss)})
            self.company_id._l10n_de_fiskaly_kassensichv_rpc('PUT', '/tss/%s' % tss_id, {'state': 'INITIALIZED', 'description': ''})

        # If the TSS has no client, create one
        client_list = self.company_id._l10n_de_fiskaly_kassensichv_rpc('GET', '/tss/%s/client' % tss_id).json()['data']
        if client_list:
            client_id = client_list[0]['_id']
        else:
            client_id = str(uuid.uuid4())
            self.company_id._l10n_de_fiskaly_kassensichv_rpc('PUT', '/tss/%s/client/%s' % (tss_id, client_id), {'serial_number': self.uuid})

        self.write({'l10n_de_fiskaly_tss_id': tss_id, 'l10n_de_fiskaly_client_id': client_id})
