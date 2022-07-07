# -*- coding: utf-8 -*-
from .common import TestMxEdiCommon, mocked_l10n_mx_edi_pac
from odoo.tests import tagged
from odoo.tools import mute_logger

from freezegun import freeze_time
from unittest.mock import patch


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestEdiResults(TestMxEdiCommon):

    # -------------------------------------------------------------------------
    # INVOICES
    # -------------------------------------------------------------------------

    def test_invoice_cfdi_no_external_trade(self):
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac):
            self.invoice.action_post()

            generated_files = self._process_documents_web_services(self.invoice, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.get_xml_tree_from_string(self.expected_invoice_cfdi_values)
            self.assertXmlTreeEqual(current_etree, expected_etree)

    def test_invoice_cfdi_group_of_taxes(self):
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac):
            self.invoice.write({
                'invoice_line_ids': [(1, self.invoice.invoice_line_ids.id, {'tax_ids': [(6, 0, self.tax_group.ids)]})],
            })
            self.invoice.action_post()

            generated_files = self._process_documents_web_services(self.invoice, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.get_xml_tree_from_string(self.expected_invoice_cfdi_values)
            self.assertXmlTreeEqual(current_etree, expected_etree)

    def test_invoice_cfdi_addenda(self):
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac):

            # Setup an addenda on the partner.
            self.invoice.partner_id.l10n_mx_edi_addenda = self.env['ir.ui.view'].create({
                'name': 'test_invoice_cfdi_addenda',
                'type': 'qweb',
                'arch': """
                    <t t-name="l10n_mx_edi.test_invoice_cfdi_addenda">
                        <test info="this is an addenda"/>
                    </t>
                """
            })

            self.invoice.action_post()

            generated_files = self._process_documents_web_services(self.invoice, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.with_applied_xpath(
                self.get_xml_tree_from_string(self.expected_invoice_cfdi_values),
                '''
                    <xpath expr="//Comprobante" position="inside">
                        <Addenda>
                            <test info="this is an addenda"/>
                        </Addenda>
                    </xpath>
                ''',
            )
            self.assertXmlTreeEqual(current_etree, expected_etree)

    def test_invoice_cfdi_mxn(self):
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac):
            self.invoice.currency_id = self.invoice.company_id.currency_id
            self.invoice.action_post()

            generated_files = self._process_documents_web_services(self.invoice, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.with_applied_xpath(
                self.get_xml_tree_from_string(self.expected_invoice_cfdi_values),
                '''
                    <xpath expr="//Comprobante" position="attributes">
                        <attribute name='Descuento'>2000.00</attribute>
                        <attribute name='Moneda'>MXN</attribute>
                        <attribute name='SubTotal'>10000.00</attribute>
                        <attribute name='Total'>8480.00</attribute>
                        <attribute name='TipoCambio' />
                    </xpath>
                    <xpath expr="//Concepto" position="attributes">
                        <attribute name='Descuento'>2000.00</attribute>
                        <attribute name='Importe'>10000.00</attribute>
                        <attribute name='ValorUnitario'>2000.00</attribute>
                    </xpath>
                    <xpath expr="//Conceptos//Traslado" position="attributes">
                        <attribute name='Base'>8000.00</attribute>
                    </xpath>
                    <xpath expr="//Conceptos//Retencion" position="attributes">
                        <attribute name='Base'>8000.00</attribute>
                    </xpath>
                    <xpath expr="//Comprobante/Impuestos" position="attributes">
                        <attribute name='TotalImpuestosRetenidos'>800.00</attribute>
                        <attribute name='TotalImpuestosTrasladados'>1280.00</attribute>
                    </xpath>
                    <xpath expr="//Comprobante/Impuestos//Retencion" position="attributes">
                        <attribute name='Importe'>800.00</attribute>
                    </xpath>
                    <xpath expr="//Comprobante/Impuestos//Traslado" position="attributes">
                        <attribute name='Importe'>1280.00</attribute>
                    </xpath>
                ''',
            )
            self.assertXmlTreeEqual(current_etree, expected_etree)

    # -------------------------------------------------------------------------
    # PAYMENTS
    # -------------------------------------------------------------------------

    def test_payment_cfdi(self):
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_payment_pac',
                   new=mocked_l10n_mx_edi_pac):
            self.payment.payment_id.action_l10n_mx_edi_force_generate_cfdi()
            self.invoice.action_post()
            self.payment.action_post()

            (self.invoice.line_ids + self.payment.line_ids)\
                .filtered(lambda line: line.account_internal_type == 'receivable')\
                .reconcile()

            # Fake the fact the invoice is signed.
            self._process_documents_web_services(self.invoice)
            self.invoice.l10n_mx_edi_cfdi_uuid = '123456789'

            generated_files = self._process_documents_web_services(self.payment.move_id, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.get_xml_tree_from_string(self.expected_payment_cfdi_values)
            self.assertXmlTreeEqual(current_etree, expected_etree)

    def test_payment_cfdi_another_currency_invoice(self):
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_payment_pac',
                   new=mocked_l10n_mx_edi_pac):
            invoice = self.env['account.move'].with_context(edi_test_mode=True).create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_a.id,
                'currency_id': self.fake_usd_data['currency'].id,
                'invoice_date': '2017-01-01',
                'date': '2017-01-01',
                'invoice_line_ids': [(0, 0, {'product_id': self.product.id, 'price_unit': 1200.0})],
            })

            self.payment.action_l10n_mx_edi_force_generate_cfdi()
            invoice.action_post()
            self.payment.action_post()

            (invoice.line_ids + self.payment.line_ids)\
                .filtered(lambda line: line.account_internal_type == 'receivable')\
                .reconcile()

            # Fake the fact the invoice is signed.
            self._process_documents_web_services(invoice)
            invoice.l10n_mx_edi_cfdi_uuid = '123456789'

            generated_files = self._process_documents_web_services(self.payment.move_id, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.with_applied_xpath(
                self.get_xml_tree_from_string(self.expected_payment_cfdi_values),
                '''
                    <xpath expr="//Complemento" position="replace">
                        <Complemento>
                            <Pagos
                                Version="1.0">
                                <Pago
                                    FechaPago="2017-01-01T12:00:00"
                                    MonedaP="Gol"
                                    Monto="8480.000"
                                    FormaDePagoP="99"
                                    TipoCambioP="0.500000">
                                    <DoctoRelacionado
                                        Folio="2"
                                        IdDocumento="123456789"
                                        ImpPagado="1200.00"
                                        ImpSaldoAnt="1200.00"
                                        ImpSaldoInsoluto="0.00"
                                        MetodoDePagoDR="PUE"
                                        MonedaDR="USD"
                                        TipoCambioDR="2.000000"
                                        NumParcialidad="1"
                                        Serie="INV/2017/"/>
                                </Pago>
                            </Pagos>
                        </Complemento>
                    </xpath>
                ''',
            )
            self.assertXmlTreeEqual(current_etree, expected_etree)

    def test_payment_cfdi_multi_currency_invoice_positive_rate(self):
        ''' Test the following payment:
        - Invoice1 & invoice2 of 750 GOL / 250 MXN in 2016.
        - Payment of 750 MXN fully paying invoice1 & invoice2 with a write-off because 1500 GOL = 750 MXN in
        2017.
        '''
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_payment_pac',
                   new=mocked_l10n_mx_edi_pac):
            invoice1 = self.env['account.move'].with_context(edi_test_mode=True).create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_a.id,
                'currency_id': self.currency_data['currency'].id,
                'invoice_date': '2016-12-31',
                'date': '2016-12-31',
                'invoice_line_ids': [(0, 0, {'product_id': self.product.id, 'price_unit': 750.0})],
            })
            invoice2 = self.env['account.move'].with_context(edi_test_mode=True).create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_a.id,
                'currency_id': self.currency_data['currency'].id,
                'invoice_date': '2016-12-31',
                'date': '2016-12-31',
                'invoice_line_ids': [(0, 0, {'product_id': self.product.id, 'price_unit': 750.0})],
            })
            (invoice1 + invoice2).action_post()

            payment = self.env['account.payment.register']\
                .with_context(
                    active_model='account.move',
                    active_ids=(invoice1 + invoice2).ids,
                    default_l10n_mx_edi_force_generate_cfdi=True,
                )\
                .create({
                    'amount': 750.0,
                    'payment_date': '2017-01-01',
                    'currency_id': self.env.company.currency_id.id,
                    'group_payment': True,
                    'payment_difference_handling': 'reconcile',
                    'writeoff_account_id': self.company_data['default_account_revenue'].id,
                    'writeoff_label': 'writeoff',
                })\
                ._create_payments()

            receivable_lines = (payment.move_id + invoice1 + invoice2).line_ids\
                .filtered(lambda x: x.account_id.internal_type == 'receivable')
            self.assertRecordValues(receivable_lines, [{'reconciled': True}] * 3)

            self._process_documents_web_services(invoice1)
            invoice1.l10n_mx_edi_cfdi_uuid = '123456789'
            self._process_documents_web_services(invoice2)
            invoice2.l10n_mx_edi_cfdi_uuid = '987654321'

            generated_files = self._process_documents_web_services(payment.move_id, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.with_applied_xpath(
                self.get_xml_tree_from_string(self.expected_payment_cfdi_values),
                '''
                    <xpath expr="//Comprobante" position="attributes">
                        <attribute name="Folio">2</attribute>
                    </xpath>
                    <xpath expr="//Complemento" position="replace">
                        <Complemento>
                            <Pagos
                                Version="1.0">
                                <Pago
                                    FechaPago="2017-01-01T12:00:00"
                                    MonedaP="MXN"
                                    Monto="750.00"
                                    NumOperacion="INV/2016/00001 INV/2016/00002"
                                    FormaDePagoP="99">
                                    <DoctoRelacionado
                                        Folio="1"
                                        IdDocumento="123456789"
                                        ImpPagado="750.000"
                                        ImpSaldoAnt="750.000"
                                        ImpSaldoInsoluto="0.000"
                                        MetodoDePagoDR="PUE"
                                        MonedaDR="Gol"
                                        TipoCambioDR="2.000000"
                                        NumParcialidad="1"
                                        Serie="INV/2016/"/>
                                    <DoctoRelacionado
                                        Folio="2"
                                        IdDocumento="987654321"
                                        ImpPagado="750.000"
                                        ImpSaldoAnt="750.000"
                                        ImpSaldoInsoluto="0.000"
                                        MetodoDePagoDR="PUE"
                                        MonedaDR="Gol"
                                        TipoCambioDR="2.000000"
                                        NumParcialidad="1"
                                        Serie="INV/2016/"/>
                                </Pago>
                            </Pagos>
                        </Complemento>
                    </xpath>
                ''',
            )
            self.assertXmlTreeEqual(current_etree, expected_etree)

    def test_payment_cfdi_multi_currency_invoice_negative_rate(self):
        ''' Test the following payment:
        - Invoice1 & invoice2 of 750 GOL / 375 MXN in 2017.
        - Payment of 500 MXN paying not completely invoice1 & invoice2 because 1500 GOL = 500 MXN in 2017.
        '''
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_payment_pac',
                   new=mocked_l10n_mx_edi_pac):

            invoice1 = self.env['account.move'].with_context(edi_test_mode=True).create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_a.id,
                'currency_id': self.currency_data['currency'].id,
                'invoice_date': '2017-01-01',
                'date': '2017-01-01',
                'invoice_line_ids': [(0, 0, {'product_id': self.product.id, 'price_unit': 750.0})],
            })
            invoice2 = self.env['account.move'].with_context(edi_test_mode=True).create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_a.id,
                'currency_id': self.currency_data['currency'].id,
                'invoice_date': '2017-01-01',
                'date': '2017-01-01',
                'invoice_line_ids': [(0, 0, {'product_id': self.product.id, 'price_unit': 750.0})],
            })
            (invoice1 + invoice2).action_post()

            payment = self.env['account.payment.register']\
                .with_context(
                    active_model='account.move',
                    active_ids=(invoice1 + invoice2).ids,
                    default_l10n_mx_edi_force_generate_cfdi=True,
                )\
                .create({
                    'amount': 500.0,
                    'payment_date': '2016-12-31',
                    'currency_id': self.env.company.currency_id.id,
                    'group_payment': True,
                    'payment_difference_handling': 'reconcile',
                    'writeoff_account_id': self.company_data['default_account_revenue'].id,
                    'writeoff_label': 'writeoff',
                })\
                ._create_payments()

            receivable_lines = (payment.move_id + invoice1 + invoice2).line_ids\
                .filtered(lambda x: x.account_id.internal_type == 'receivable')
            self.assertRecordValues(receivable_lines, [
                {'reconciled': True},
                {'reconciled': True},
                {'reconciled': True},
            ])

            self._process_documents_web_services(invoice1)
            invoice1.l10n_mx_edi_cfdi_uuid = '123456789'
            self._process_documents_web_services(invoice2)
            invoice2.l10n_mx_edi_cfdi_uuid = '987654321'

            generated_files = self._process_documents_web_services(payment.move_id, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.with_applied_xpath(
                self.get_xml_tree_from_string(self.expected_payment_cfdi_values),
                '''
                    <xpath expr="//Comprobante" position="attributes">
                        <attribute name="Folio">1</attribute>
                        <attribute name="Serie">BNK1/2016/12/</attribute>
                    </xpath>
                    <xpath expr="//Complemento" position="replace">
                        <Complemento>
                            <Pagos
                                Version="1.0">
                                <Pago
                                    FechaPago="2016-12-31T12:00:00"
                                    MonedaP="MXN"
                                    Monto="500.00"
                                    NumOperacion="INV/2017/00002 INV/2017/00003"
                                    FormaDePagoP="99">
                                    <DoctoRelacionado
                                        Folio="2"
                                        IdDocumento="123456789"
                                        ImpPagado="750.000"
                                        ImpSaldoAnt="750.000"
                                        ImpSaldoInsoluto="0.000"
                                        MetodoDePagoDR="PUE"
                                        MonedaDR="Gol"
                                        TipoCambioDR="3.000000"
                                        NumParcialidad="1"
                                        Serie="INV/2017/"/>
                                    <DoctoRelacionado
                                        Folio="3"
                                        IdDocumento="987654321"
                                        ImpPagado="750.000"
                                        ImpSaldoAnt="750.000"
                                        ImpSaldoInsoluto="0.000"
                                        MetodoDePagoDR="PUE"
                                        MonedaDR="Gol"
                                        TipoCambioDR="3.000000"
                                        NumParcialidad="1"
                                        Serie="INV/2017/"/>
                                </Pago>
                            </Pagos>
                        </Complemento>
                    </xpath>
                ''',
            )
            self.assertXmlTreeEqual(current_etree, expected_etree)

    def test_payment_cfdi_rate(self):
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_payment_pac',
                   new=mocked_l10n_mx_edi_pac):

            self.fake_usd_data['rates'][0].rate = 0.050498164392
            self.fake_usd_data['rates'][1].rate = 0.050465035300

            invoice1 = self.env['account.move'].with_context(edi_test_mode=True).create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_a.id,
                'currency_id': self.fake_usd_data['currency'].id,
                'invoice_date': '2016-12-31',
                'date': '2016-12-31',
                'invoice_line_ids': [(0, 0, {'product_id': self.product.id, 'price_unit': 81.20})],
            })
            invoice2 = self.env['account.move'].with_context(edi_test_mode=True).create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_a.id,
                'currency_id': self.fake_usd_data['currency'].id,
                'invoice_date': '2016-12-31',
                'date': '2016-12-31',
                'invoice_line_ids': [(0, 0, {'product_id': self.product.id, 'price_unit': 81.20})],
            })
            (invoice1 + invoice2).action_post()

            payment = self.env['account.payment.register']\
                .with_context(
                    active_model='account.move',
                    active_ids=(invoice1 + invoice2).ids,
                    default_l10n_mx_edi_force_generate_cfdi=True,
                )\
                .create({
                    'amount': 3215.96,
                    'payment_date': '2017-01-01',
                    'currency_id': self.env.company.currency_id.id,
                    'group_payment': True,
                })\
                ._create_payments()

            receivable_lines = (payment.move_id + invoice1 + invoice2).line_ids\
                .filtered(lambda x: x.account_id.internal_type == 'receivable')
            self.assertRecordValues(receivable_lines, [
                {'reconciled': True},
                {'reconciled': True},
                {'reconciled': True},
            ])

            self._process_documents_web_services(invoice1)
            invoice1.l10n_mx_edi_cfdi_uuid = '123456789'
            self._process_documents_web_services(invoice2)
            invoice2.l10n_mx_edi_cfdi_uuid = '987654321'

            generated_files = self._process_documents_web_services(payment.move_id, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.with_applied_xpath(
                self.get_xml_tree_from_string(self.expected_payment_cfdi_values),
                '''
                    <xpath expr="//Comprobante" position="attributes">
                        <attribute name="Folio">2</attribute>
                        <attribute name="Serie">BNK1/2017/01/</attribute>
                    </xpath>
                    <xpath expr="//Complemento" position="replace">
                        <Complemento>
                            <Pagos
                                Version="1.0">
                                <Pago
                                    FechaPago="2017-01-01T12:00:00"
                                    MonedaP="MXN"
                                    Monto="3215.96"
                                    NumOperacion="INV/2016/00001 INV/2016/00002"
                                    FormaDePagoP="99">
                                    <DoctoRelacionado
                                        Folio="1"
                                        IdDocumento="123456789"
                                        ImpPagado="81.20"
                                        ImpSaldoAnt="81.20"
                                        ImpSaldoInsoluto="0.00"
                                        MetodoDePagoDR="PUE"
                                        MonedaDR="USD"
                                        TipoCambioDR="0.050498"
                                        NumParcialidad="1"
                                        Serie="INV/2016/"/>
                                    <DoctoRelacionado
                                        Folio="2"
                                        IdDocumento="987654321"
                                        ImpPagado="81.20"
                                        ImpSaldoAnt="81.20"
                                        ImpSaldoInsoluto="0.00"
                                        MetodoDePagoDR="PUE"
                                        MonedaDR="USD"
                                        TipoCambioDR="0.050498"
                                        NumParcialidad="1"
                                        Serie="INV/2016/"/>
                                </Pago>
                            </Pagos>
                        </Complemento>
                    </xpath>
                ''',
            )
            self.assertXmlTreeEqual(current_etree, expected_etree)

    # -------------------------------------------------------------------------
    # STATEMENT LINES
    # -------------------------------------------------------------------------

    def test_statement_line_cfdi(self):
        with freeze_time(self.frozen_today), \
             mute_logger('py.warnings'), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_invoice_pac',
                   new=mocked_l10n_mx_edi_pac), \
             patch('odoo.addons.l10n_mx_edi.models.account_edi_format.AccountEdiFormat._l10n_mx_edi_post_payment_pac',
                   new=mocked_l10n_mx_edi_pac):
            self.statement_line.action_l10n_mx_edi_force_generate_cfdi()
            self.invoice.action_post()
            self.statement.button_post()

            receivable_line = self.invoice.line_ids.filtered(lambda line: line.account_internal_type == 'receivable')
            self.statement_line.reconcile([{'id': receivable_line.id}])

            # Fake the fact the invoice is signed.
            self._process_documents_web_services(self.invoice)
            self.invoice.l10n_mx_edi_cfdi_uuid = '123456789'

            generated_files = self._process_documents_web_services(self.statement_line.move_id, {'cfdi_3_3'})
            self.assertTrue(generated_files)
            cfdi = generated_files[0]

            current_etree = self.get_xml_tree_from_string(cfdi)
            expected_etree = self.with_applied_xpath(
                self.get_xml_tree_from_string(self.expected_payment_cfdi_values),
                '''
                    <xpath expr="//Comprobante" position="attributes">
                        <attribute name="Folio">2</attribute>
                    </xpath>
                ''',
            )
            self.assertXmlTreeEqual(current_etree, expected_etree)
