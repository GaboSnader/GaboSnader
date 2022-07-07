import logging
from odoo import models, api, _

_logger = logging.getLogger(__name__)


class WizardAccountingAssistant(models.TransientModel):
    _inherit = 'wizard.accounting.assistant'


    def send(self):

        domain = [
            ('date', '>=', self.date_inicio),
            ('date', '<=', self.date_fin)
        ]

        if self.account_id:
            domain.append(('account_id', '=', self.account_id.id))

        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))

        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))

        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))

        if self.branch_ids:
            domain.append(('sucursal', 'in', self.branch_ids.ids))

        if self.negocio:
            domain.append(('negocio', 'in', self.negocio.ids))

        if self.area:
            domain.append(('area', 'in', self.area.ids))

        if self.department:
            domain.append(('department', 'in', self.department.ids))

        if self.equipo:
            domain.append(('equipo', 'in', self.equipo.ids))

        if self.tipo_operacion:
            domain.append(('tipo_operacion', 'in', self.tipo_operacion.ids))

        tree_view_ref = ('account.view_move_line_tree')
        form_view_ref = ('account.view_move_line_form')
        tree_view = self.env.ref(tree_view_ref, raise_if_not_found=False)
        form_view = self.env.ref(form_view_ref, raise_if_not_found=False)

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Apuntes Contables'),
            'res_model': 'account.move.line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'domain': domain,
        }

        if tree_view and form_view:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
        return action
