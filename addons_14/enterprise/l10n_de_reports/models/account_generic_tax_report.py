from odoo import models, fields, _
from odoo.exceptions import UserError
from lxml import etree
from datetime import date, datetime


class AccountGenericTaxReport(models.AbstractModel):
    _inherit = 'account.generic.tax.report'

    def _get_reports_buttons(self):
        buttons = super(AccountGenericTaxReport, self)._get_reports_buttons()
        if self.env.company.country_id.code == 'DE':
            buttons += [{'name': _('Export (XML)'), 'sequence': 3, 'action': 'print_xml', 'file_export_type': _('XML')}]
        return buttons

    def get_xml(self, options):
        ctx = self._set_context(options)
        report_lines = self.with_context(ctx)._get_lines(options)

        de_tax_report = self.env.ref('l10n_de.tax_report')
        report_lines_have_codes = self.env['account.tax.report.line'].search([('report_id', '=', de_tax_report.id), ('code', '!=', None)], limit=1)
        if not self.env.ref('l10n_de_reports.tax_export_xml', raise_if_not_found=False) or not report_lines_have_codes:
            raise UserError('The template of the report has not been found, please update modules "l10n_de" and "l10n_de_reports".')

        template_context = {}
        date_to = datetime.strptime(options['date']['date_to'], '%Y-%m-%d')
        template_context['year'] = date_to.year
        if options['date']['period_type'] == 'month':
            template_context['period'] = date_to.month
        elif options['date']['period_type'] == 'quarter':
            month_end = int(date_to.month)
            if month_end % 3 != 0:
                raise ValueError('Quarter not supported')
            # For quarters, the period should be 41, 42, 43, 44 depending on the quarter.
            template_context['period'] = int(month_end / 3 + 40)
        template_context['creation_date'] = date.today().strftime("%Y%m%d")
        template_context['company'] = self.env.company

        qweb = self.env['ir.qweb']
        doc = qweb._render('l10n_de_reports.tax_export_xml', values=template_context)
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(doc, parser)

        taxes = tree.xpath('//Umsatzsteuervoranmeldung')[0]
        # Add the values dynamically. We do it here because the tag is generated from the code and
        # Qweb doesn't allow dynamically generated tags.
        for line in report_lines:
            if line['line_code'] and line['columns'][0]['balance']:
                elem = etree.SubElement(taxes, "kz" + line['line_code'])
                elem.text = str(line['columns'][0]['balance'])

        return etree.tostring(tree, pretty_print=True, standalone=False, encoding='ISO-8859-1',)
