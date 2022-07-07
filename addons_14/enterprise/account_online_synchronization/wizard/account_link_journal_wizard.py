# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountLinkJournalLine(models.TransientModel):
    _name = "account.link.journal.line"
    _description = "Link one bank account to a journal"

    action = fields.Selection([('create', 'Create new journal'), ('link', 'Link to existing journal')], default='create')
    journal_id = fields.Many2one('account.journal', domain="[('type', '=', 'bank'), ('account_online_account_id', '=', False)]")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    online_account_id = fields.Many2one('account.online.account')
    name = fields.Char(related='online_account_id.name', string="Account name", readonly=False)
    balance = fields.Float(related='online_account_id.balance', readonly=True)
    account_online_wizard_id = fields.Many2one('account.link.journal')
    account_number = fields.Char(related='online_account_id.account_number', readonly=False)
    journal_statements_creation = fields.Selection(selection=lambda x: x.env['account.journal']._get_statement_creation_possible_values(),
        default='month', string="Synchronization frequency", required=True)

    def unlink(self):
        self.mapped('online_account_id').filtered(lambda acc: not acc.journal_ids).unlink()
        return super(AccountLinkJournalLine, self).unlink()

    @api.onchange('journal_id')
    def _onchange_action(self):
        if self.journal_id:
            self.journal_statements_creation = self.journal_id.bank_statement_creation_groupby
            self.action = 'link'
        else:
            self.journal_statements_creation = 'month'
            self.action = 'create'


class AccountLinkJournal(models.TransientModel):
    _name = "account.link.journal"
    _description = "Link list of bank accounts to journals"

    number_added = fields.Integer(readonly=True)
    transactions = fields.Html(readonly=True)
    sync_date = fields.Date('Get transactions since', default=lambda a: fields.Date.context_today(a) - relativedelta(days=15))
    account_ids = fields.One2many('account.link.journal.line', 'account_online_wizard_id', 'Synchronized accounts')

    def unlink(self):
        self.mapped('account_ids').unlink()
        return super(AccountLinkJournal, self).unlink()

    def _get_journal_values(self, account, create=False):
        vals = {
            'account_online_account_id': account.online_account_id.id,
            'bank_statements_source': 'online_sync',
            'currency_id': account.currency_id.id,
        }
        if account.account_number:
            vals['bank_acc_number'] = account.account_number
        if create:
            vals['name'] = account.name
            vals['type'] = 'bank'
            vals['bank_statement_creation_groupby'] = account.journal_statements_creation
        else:
            vals['bank_statement_creation_groupby'] = account.journal_id.bank_statement_creation_groupby or account.journal_statements_creation
        return vals

    def sync_now(self):
        '''
        This method is called when the user click on "Synchronize now".
        '''
        # Link account to journal
        journal_already_linked = []
        if not len(self.account_ids):
            return {'type': 'ir.actions.act_window_close'}
        for account in self.account_ids:
            account.online_account_id.write({'last_sync': self.sync_date})
            if account.journal_id:
                if account.journal_id.id in journal_already_linked:
                    raise UserError(_('You can not link two accounts to the same journal.'))
                journal_already_linked.append(account.journal_id.id)
                account.journal_id.write(self._get_journal_values(account))
            else:
                vals = self._get_journal_values(account, create=True)
                self.env['account.journal'].create(vals)
        # Call to synchronize
        online_account_ids = self.account_ids.mapped('online_account_id')
        return online_account_ids.mapped('account_online_link_id').action_fetch_transactions()

    def cancel_sync(self):
        # Remove account_online_account if the user cancel the link
        self.account_ids.unlink()
        return {'type': 'ir.actions.act_window_close'}
