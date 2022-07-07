# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        res = super(MailComposeMessage, self).default_get(fields)
        _logger.debug("context => %r" % self.env.context)
        attachment_ids = self.env.context.get('attachment_ids', False)
        if attachment_ids and len(attachment_ids) >= 1:
            res.update({'attachment_ids': [(6, 0, attachment_ids)]})
        return res
