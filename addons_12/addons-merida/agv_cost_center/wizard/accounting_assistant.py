from odoo import models, fields,  _


class WizardAccountingAssistant(models.TransientModel):
    _name = 'wizard.accounting.assistant'
    _description = 'Accounting Assistant Wizard'

    account_id = fields.Many2one('account.account')
    journal_ids = fields.Many2many('account.journal')
    date_begin = fields.Date(required=True)
    date_end = fields.Date(required=True)

    warehouse_ids = fields.Many2many('stock.warehouse')
    business_ids = fields.Many2many('cost_center.business')
    area_ids = fields.Many2many('cost_center.area')
    department_ids = fields.Many2many('hr.department')
    equipment_ids = fields.Many2many('cost_center.equipment')
    type_of_operation_ids = fields.Many2many('cost_center.type_of_operation')
    partner_id = fields.Many2one('res.partner')
    product_id = fields.Many2one('product.product')
    group_by = fields.Selection([
        ('none', 'None'),
        ('account', 'Account'),
        ('partner', 'Partner'),
    ], default='none')

    # def send(self):
    # No tendría sentido agrupar su ya se seleccionó una cuenta o una empresa
    # if self.account_id and self.agrupamiento == 'cuenta':
    #     self.agrupamiento = 'ninguna'
    # if self.partner_id and self.agrupamiento == 'empresa':
    #     self.agrupamiento = 'ninguna'
    #     mv_ids = False
    #     move_ids = []
    #     move_objetcs_ids = []
    #     jr_val = False
    #     sc_val = False
    #     ng_val = False
    #     ar_val = False
    #     dp_val = False
    #     eq_val = False
    #     tp_val = False
    #     partner_val = False
    #     product_val = False
    #     mv_ids = self.env['account.move.line']
    #     if self.account_id:
    #         mv_ids = mv_ids.search([('account_id', '=', self.account_id.id)])
    #     else:
    #         mv_ids = mv_ids.search([])
    #     for mv in mv_ids:
    #         if mv.parent_state == 'posted':
    #             if mv.date >= self.date_inicio and mv.date <= self.date_fin:
    #                 if self.journal_ids:
    #                     for jr in self.journal_ids:
    #                         if jr.id == mv.journal_id.id:
    #                             jr_val = True
    #                             break
    #                         else:
    #                             jr_val = False
    #                 else:
    #                     jr_val = True
    #                 if self.partner_id:
    #                     for partner in self.partner_id:
    #                         if partner.id == mv.partner_id.id:
    #                             partner_val = True
    #                         else:
    #                             partner_val = False
    #                 else:
    #                     partner_val = True
    #                 if self.product_id:
    #                     for product in self.product_id:
    #                         if product.id == mv.product_id.id:
    #                             product_val = True
    #                         else:
    #                             product_val = False
    #                 else:
    #                     product_val = True

    #                 if self.branch_ids:
    #                     for sc in self.branch_ids:
    #                         if sc.id == mv.sucursal.id:
    #                             sc_val = True
    #                             break
    #                         else:
    #                             sc_val = False
    #                 else:
    #                     sc_val = True

    #                 if self.negocio:
    #                     for ng in self.negocio:
    #                         if ng.id == mv.negocio.id:
    #                             ng_val = True
    #                             break
    #                         else:
    #                             ng_val = False
    #                 else:
    #                     ng_val = True

    #                 if self.area:
    #                     for ar in self.area:
    #                         if ar.id == mv.area.id:
    #                             ar_val = True
    #                             break
    #                         else:
    #                             ar_val = False
    #                 else:
    #                     ar_val = True

    #                 if self.department:
    #                     for dp in self.department:
    #                         if dp.id == mv.department.id:
    #                             dp_val = True
    #                             break
    #                         else:
    #                             dp_val = False
    #                 else:
    #                     dp_val = True

    #                 if self.equipo:
    #                     for eq in self.equipo:
    #                         if eq.id == mv.equipo.id:
    #                             eq_val = True
    #                             break
    #                         else:
    #                             eq_val = False
    #                 else:
    #                     eq_val = True

    #                 if self.tipo_operacion:
    #                     for tp in self.tipo_operacion:
    #                         if tp.id == mv.tipo_operacion.id:
    #                             tp_val = True
    #                             break
    #                         else:
    #                             tp_val = False
    #                 else:
    #                     tp_val = True

    #                 if jr_val and sc_val and ng_val and ar_val and dp_val and eq_val and tp_val and partner_val and product_val:
    #                     # move_ids.append(mv.id)
    #                     move_objetcs_ids.append(mv)

    #     move_objetcs_ids.sort(key=operator.attrgetter('id'))

    #     move_objetcs_ids.sort(key=operator.attrgetter('date'))
    #     for m in move_objetcs_ids:
    #         move_ids.append(m.id)
    #     if self.agrupamiento == 'ninguna':
    #         self.get_saldos(move_objetcs_ids, self.agrupamiento)
    #         return {
    #             'name': _('Auxiliar Contable View'),
    #             'view_type': 'form',
    #             'view_mode': 'tree',
    #             'res_model': 'account.move.line',
    #             'view_id': self.env['ir.ui.view'].search([('name', '=', 'view.auxiliar.contable.mods')], limit=1).id,
    #             'type': 'ir.actions.act_window',
    #             'domain': [('id', 'in', move_ids)],
    #         }
    #     elif self.agrupamiento == 'cuenta':

    #         move_objetcs_ids.sort(key=operator.attrgetter('account_id.id'))

    #         self.get_saldos(move_objetcs_ids, self.agrupamiento)
    #         return {
    #             'name': _('Auxiliar Contable View'),
    #             'view_type': 'form',
    #             'view_mode': 'tree',
    #             'res_model': 'account.move.line',
    #             'view_id': self.env['ir.ui.view'].search([('name', '=', 'view.auxiliar.contable.mods')], limit=1).id,
    #             'type': 'ir.actions.act_window',
    #             'domain': [('id', 'in', move_ids)],
    #             'context': {'group_by': 'account_id'},
    #         }
    #     elif self.agrupamiento == 'empresa':
    #         move_objetcs_ids.sort(key=operator.attrgetter('partner_id.id'))

    #         self.get_saldos(move_objetcs_ids, self.agrupamiento)
    #         return {
    #             'name': _('Auxiliar Contable View'),
    #             'view_type': 'form',
    #             'view_mode': 'tree',
    #             'res_model': 'account.move.line',
    #             'view_id': self.env['ir.ui.view'].search([('name', '=', 'view.auxiliar.contable.mods')], limit=1).id,
    #             'type': 'ir.actions.act_window',
    #             'domain': [('id', 'in', move_ids)],
    #             'context': {'group_by': 'partner_id'},
    #         }

    # def get_saldos(self, movimento_ids, grupo):
    #     if movimento_ids:
    #         # Esto es a lo que Luis llama Z infinita
    #         if len(movimento_ids) == 1:
    #             primer_saldo = self.get_primer_saldo_inicial(
    #                 movimento_ids[0].date, False, False)
    #             print('PRIMER SALDO Inicial SOLO UN RESULTADO::', primer_saldo)
    #             movimento_ids[0].saldo_inicial = primer_saldo
    #             self.get_saldo_inicial_final(movimento_ids[0])

    #         elif len(movimento_ids) > 1 and grupo == 'ninguna':
    #             primer_saldo = self.get_primer_saldo_inicial(
    #                 movimento_ids[0].date, False, False)
    #             print('PRIMER SALDO Inicial NINGUN GRUPO::', primer_saldo)
    #             movimento_ids[0].saldo_inicial = primer_saldo
    #             # print('id del primer registro',movimento_ids[0].id)
    #             # print('primer registro, saldo inicial',movimento_ids[0].saldo_inicial)
    #             self.get_saldo_inicial_final(movimento_ids[0])
    #             for n in range(len(movimento_ids)):
    #                 if n > 0:
    #                     movimento_ids[n].saldo_inicial = movimento_ids[n-1].saldo_final
    #                     #print('id - %i ' % (movimento_ids[n].id))
    #                     self.get_saldo_inicial_final(movimento_ids[n])

    #         elif len(movimento_ids) > 1 and grupo == 'cuenta':
    #             primer_saldo = self.get_primer_saldo_inicial(
    #                 movimento_ids[0].date, movimento_ids[0].account_id.id, False)

    #             # obtiene el primer saldo
    #             movimento_ids[0].saldo_inicial = primer_saldo
    #             self.get_saldo_inicial_final(movimento_ids[0])

    #             for n in range(len(movimento_ids)):
    #                 if n > 0:  # Si el elemento actual tiene la misma cuenta que el anterior, se pone el Saldo inicial como el Saldo final del registro anterior
    #                     if movimento_ids[n].account_id.id == movimento_ids[n-1].account_id.id:
    #                         movimento_ids[n].saldo_inicial = movimento_ids[n-1].saldo_final
    #                         self.get_saldo_inicial_final(movimento_ids[n])
    #                     else:  # Si el elemento actual tiene diferente cuenta que el anterior, se calcula de nuevo un Saldo inicial con la cuenta del grupo
    #                         primer_saldo_grupo = self.get_primer_saldo_inicial(
    #                             movimento_ids[n].date, movimento_ids[n].account_id.id, False)
    #                         movimento_ids[n].saldo_inicial = primer_saldo_grupo
    #                         self.get_saldo_inicial_final(movimento_ids[n])
    #         elif len(movimento_ids) > 1 and grupo == 'empresa':
    #             primer_saldo = self.get_primer_saldo_inicial(
    #                 movimento_ids[0].date, False, False)
    #             # obtiene el primer saldo
    #             movimento_ids[0].saldo_inicial = primer_saldo
    #             self.get_saldo_inicial_final(movimento_ids[0])
    #             print('PRIMER SALDO INICIAL x Empresa:: id - %i , es de:: %d' %
    #                   (movimento_ids[0].id, movimento_ids[0].saldo_inicial))
    #             for n in range(len(movimento_ids)):
    #                 if n>0: #Si el elemento actual tiene la misma empresa que el anterior, se pone el Saldo inicial como el Saldo final del registro anterior
    #                     if movimento_ids[n].partner_id.id == movimento_ids[n-1].partner_id.id:
    #                         print('id - %i ' % (movimento_ids[n].id))
    #                         movimento_ids[n].saldo_inicial = movimento_ids[n-1].saldo_final
    #                         self.get_saldo_inicial_final(movimento_ids[n])
    #                     else: # Si el elemento actual tiene diferente empresa que el anterior, se calcula de nuevo un Saldo inicial con la empresa del grupo
    #                         print('id - %i ' % (movimento_ids[n].id)) #REVISAR AQUI TODO
    #                         primer_saldo_grupo = self.get_primer_saldo_inicial(movimento_ids[n].date, False, movimento_ids[n].partner_id.id)
    #                         movimento_ids[n].saldo_inicial = primer_saldo_grupo
    #                         self.get_saldo_inicial_final(movimento_ids[n])

    # #Se hace una operación similar a la realizada para obtener los ids para la vista,
    # # sólo que ahora se requiere para todos los elementos anteriores a la fecha
    # def get_primer_saldo_inicial(self, fecha, cuenta, partner):
    #     saldo = 0
    #     #Se hace el procesamiento anterior, pero ahora se verifica si hay agrupamientos
    #     if self.account_id and not cuenta and not partner:
    #         print('PRIMER SALDO CON CUENTA NO REQUIERE GRUPOS')
    #         mv_ids = self.env['account.move.line'].search([('account_id','=',self.account_id.id),('date', '<', fecha)])
    #     elif not self.account_id and not cuenta and not partner:
    #         print('PRIMER SALDO SIN CUENTA NO REQUIERE GRUPOS')
    #         mv_ids = self.env['account.move.line'].search([('date', '<', fecha)])
    #     #Este será en el caso de que haya agrupamiento por cuenta, y se tenga que sacar el primer saldo por cada grupo
    #     elif cuenta:
    #         print('PRIMER SALDO PARA ALGUNA CUENTA',cuenta)
    #         mv_ids = self.env['account.move.line'].search([('account_id','=',cuenta),('date', '<', fecha)])
    #     elif partner:
    #         print('PRIMER SALDO PARA ALGUNA EMPRESA', partner)
    #         mv_ids = self.env['account.move.line'].search([('partner_id','=',partner),('date', '<', fecha)])
    #     for mv in mv_ids:
    #         if mv.parent_state == 'posted':
    #             if self.journal_ids:
    #                 for jr in self.journal_ids:
    #                     if jr.id == mv.journal_id.id:
    #                         jr_val = True
    #                         break
    #                     else:
    #                         jr_val = False
    #             else:
    #                 jr_val = True
    #             if self.partner_id:
    #                 for partner in self.partner_id:
    #                     if partner.id == mv.partner_id.id:
    #                         partner_val = True
    #                     else:
    #                         partner_val = False
    #             else:
    #                 partner_val = True
    #             if self.product_id:
    #                 for product in self.product_id:
    #                     if product.id == mv.product_id.id:
    #                         product_val = True
    #                     else:
    #                         product_val = False
    #             else:
    #                 product_val = True

    #             if self.branch_ids:
    #                 for sc in self.branch_ids:
    #                     if sc.id == mv.sucursal.id:
    #                         sc_val = True
    #                         break
    #                     else:
    #                         sc_val = False
    #             else:
    #                 sc_val = True

    #             if self.negocio:
    #                 for ng in self.negocio:
    #                     if ng.id == mv.negocio.id:
    #                         ng_val = True
    #                         break
    #                     else:
    #                         ng_val = False
    #             else:
    #                 ng_val = True

    #             if self.area:
    #                 for ar in self.area:
    #                     if ar.id == mv.area.id:
    #                         ar_val = True
    #                         break
    #                     else:
    #                         ar_val = False
    #             else:
    #                 ar_val = True

    #             if self.department:
    #                 for dp in self.department:
    #                     if dp.id == mv.department.id:
    #                         dp_val = True
    #                         break
    #                     else:
    #                         dp_val = False
    #             else:
    #                 dp_val = True

    #             if self.equipo:
    #                 for eq in self.equipo:
    #                     if eq.id == mv.equipo.id:
    #                         eq_val = True
    #                         break
    #                     else:
    #                         eq_val = False
    #             else:
    #                 eq_val = True

    #             if self.tipo_operacion:
    #                 for tp in self.tipo_operacion:
    #                     if tp.id == mv.tipo_operacion.id:
    #                         tp_val = True
    #                         break
    #                     else:
    #                         tp_val = False
    #             else:
    #                 tp_val = True

    #             if jr_val and sc_val and ng_val and ar_val and dp_val and eq_val and tp_val and partner_val and product_val:
    #                 if mv.account_id.tag_ids:
    #                     if mv.account_id.tag_ids[0].nature == 'D':
    #                         # print('Movimiento con naturaleza DEUDORA',mv.id)
    #                         # print('debe',mv.debit)
    #                         # print('haber',mv.credit)
    #                         saldo += mv.debit - mv.credit
    #                     elif mv.account_id.tag_ids[0].nature == 'A':
    #                         # print('Movimiento con naturaleza ACREEDORA',mv.id)
    #                         # print('debe',mv.debit)
    #                         # print('haber',mv.credit)
    #                         saldo += mv.debit - mv.credit
    #                     else:
    #                         print('NO TIENE NATURALEZA, no realiza operación')
    #                     print('saldo',saldo)
    #     return saldo

    # def get_saldo_inicial_final(self, move): #Obtener saldo final con base en el inicial
    #     if move.account_id.tag_ids:
    #         if move.account_id.tag_ids[0].nature == 'D': #Se toma la primer etiqueta que se encuentra
    #             print("ES DEUDORA")
    #             move.saldo_final = move.saldo_inicial +  move.debit - move.credit
    #             print('id - %i , inicial - %d , debito - %d, credito - %d, final - %d' % (move.id, move.saldo_inicial,move.debit,move.credit,move.saldo_final))
    #             print("SALDO FINAL0::",move.saldo_final)
    #         elif move.account_id.tag_ids[0].nature == 'A': #Se toma la primer etiqueta que se encuentra
    #             print("ES ACREEDORA0")
    #             move.saldo_final = move.saldo_inicial - move.debit + move.credit
    #             print("SALDO FINAL0::",move.saldo_final)
    #         else:
    #             print('NO TIENE NATURALEZA')
    #     else:
    #         print('REGISTRO NO TIENE ETIQUETAS:')
    #         print('id - %i , inicial - %d , debito - %d, credito - %d, final - %d' % (move.id, move.saldo_inicial,move.debit,move.credit,move.saldo_final))
    #         move.saldo_final = move.saldo_inicial

    def send(self):

        domain = [
            ('date', '>=', self.date_begin),
            ('date', '<=', self.date_end)
        ]

        if self.account_id:
            domain.append(('account_id', '=', self.account_id.id))

        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))

        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))

        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))

        if self.warehouse_ids:
            domain.append(('warehouse_id', 'in', self.warehouse_ids.ids))

        if self.business_ids:
            domain.append(('business_id', 'in', self.business_ids.ids))

        if self.area_ids:
            domain.append(('area_id', 'in', self.area_ids.ids))

        if self.department_ids:
            domain.append(('preference_department_id',
                          'in', self.department_ids.ids))

        if self.equipment_ids:
            domain.append(('equipment_id', 'in', self.equipment_ids.ids))

        if self.type_of_operation_ids:
            domain.append(('type_of_operation_id', 'in',
                          self.type_of_operation_ids.ids))

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
