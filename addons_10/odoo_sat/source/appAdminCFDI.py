#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

import os
import sys
import time
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QDialog,
    QAction,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QAbstractItemView,
    QGroupBox,
    QComboBox,
    QButtonGroup,
    QRadioButton,
    QSpinBox,
    QDateEdit,
    QSplashScreen,
    QDesktopWidget,
    QCheckBox,
)
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QSize, QEvent, QTimer, QUrl, QRect

from settings import log, WEBSITE, W_DONATE, W_FORUM
from sat.db import create_tables, get_companies, save_company, delete_company, \
    get_invoices, get_emisores, get_years, get_months, delete_invoice, \
    update_status
from sat import db
from sat import util


TITLE = 'Empresa Libre - Admin CFDI'
TYPE_CFDI = {
    'Todos': '-1',
    'Estandar': '8',
    'Nómina 1.1': '1048576',
    'Nómina 1.2': '137438953472',
}
YELLOW = ' { background-color: #FFFACD }'
WHITE = ' { background-color: white }'


def warning(msg):
    msgbox = QMessageBox()
    msgbox.setIcon(QMessageBox.Critical)
    msgbox.setWindowTitle(TITLE)
    msgbox.setText(msg)
    msgbox.setStandardButtons(QMessageBox.Ok)
    msgbox.exec()
    return


def msgbox(msg):
    msgbox = QMessageBox()
    msgbox.setIcon(QMessageBox.Information)
    msgbox.setWindowTitle(TITLE)
    msgbox.setText(msg)
    msgbox.setStandardButtons(QMessageBox.Ok)
    msgbox.exec()
    return


def question(msg):
    result = QMessageBox.question(
        None, TITLE, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    return result == QMessageBox.Yes


def validate_write(path):
    if os.access(path, os.W_OK):
        return True
    msg = 'No tienes derechos de escritura en el directorio seleccionado'
    warning(msg)
    return False


def validate_text(value):
    if value:
        return True
    msg = 'El campo es requerido'
    warning(msg)
    return False


class DlgCompanies(QDialog):
    TITLE = 'Empresas'

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._init_data()
        self.exec()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            color = obj.metaObject().className() + YELLOW
            obj.setStyleSheet(color);
        elif event.type() == QEvent.FocusOut:
            color = obj.metaObject().className() + WHITE
            obj.setStyleSheet(color);
        return False

    def _init_ui(self):
        self.setWindowTitle(self.TITLE)
        self.cmd_close = QPushButton('Cerrar')
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self._table_companies())

        vbox1 = QVBoxLayout()
        lbl_rfc = QLabel('RFC')
        self.txt_rfc = QLineEdit()
        self.txt_rfc.setMaxLength(13)
        self.txt_rfc.setMinimumWidth(350)
        self.txt_rfc.setReadOnly(True)
        lbl_name = QLabel('Razón Social')
        self.txt_name = QLineEdit()
        self.txt_name.setReadOnly(True)
        lbl_ciec = QLabel('Clave CIEC')
        self.txt_ciec = QLineEdit()
        self.txt_ciec.setEchoMode(QLineEdit.Password)
        self.txt_ciec.setReadOnly(True)
        lbl_path = QLabel('Ruta de descarga')
        hb_path = QHBoxLayout()
        self.txt_path = QLineEdit()
        self.txt_path.setReadOnly(True)
        self.cmd_path = QPushButton('...')
        self.cmd_path.setMaximumWidth(30)
        self.cmd_path.setEnabled(False)
        hb_path.addWidget(self.txt_path)
        hb_path.addWidget(self.cmd_path)

        vbox1.addWidget(lbl_rfc)
        vbox1.addWidget(self.txt_rfc)
        vbox1.addWidget(lbl_name)
        vbox1.addWidget(self.txt_name)
        vbox1.addWidget(lbl_ciec)
        vbox1.addWidget(self.txt_ciec)
        vbox1.addWidget(lbl_path)
        vbox1.addLayout(hb_path)
        vbox1.addStretch(1)

        vbox2 = QVBoxLayout()
        self.cmd_new = QPushButton('Nuevo')
        self.cmd_save = QPushButton('Guardar')
        self.cmd_edit = QPushButton('Editar')
        self.cmd_update = QPushButton('Actualizar')
        self.cmd_delete = QPushButton('Eliminar')
        self.cmd_cancel = QPushButton('Cancelar')
        self.cmd_save.setEnabled(False)
        self.cmd_edit.setEnabled(False)
        self.cmd_update.setEnabled(False)
        self.cmd_delete.setEnabled(False)
        self.cmd_cancel.setEnabled(False)

        vbox2.addWidget(self.cmd_new)
        vbox2.addWidget(self.cmd_save)
        vbox2.addWidget(self.cmd_edit)
        vbox2.addWidget(self.cmd_update)
        vbox2.addWidget(self.cmd_delete)
        vbox2.addWidget(self.cmd_cancel)
        vbox2.addStretch(1)

        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)

        vbox.addLayout(hbox)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.cmd_close)
        hbox1.addStretch(1)

        vbox.addLayout(hbox1)
        self.setLayout(vbox)

        self.cmd_new.clicked.connect(self._new)
        self.cmd_save.clicked.connect(self._save)
        self.cmd_cancel.clicked.connect(self._cancel)
        self.cmd_path.clicked.connect(self._select_path)
        self.cmd_close.clicked.connect(self._close)
        self.cmd_delete.clicked.connect(self._delete)

        self.txt_rfc.installEventFilter(self)
        self.txt_name.installEventFilter(self)
        self.txt_ciec.installEventFilter(self)
        self.txt_path.installEventFilter(self)
        return

    def _table_companies(self):
        headers = ('id', 'RFC', 'Razón Social', 'CIEC', 'Ruta')
        self.table = QTableWidget()
        self.table.setMinimumWidth(400)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnCount(5)
        self.table.setColumnHidden(0, True)
        self.table.setColumnHidden(3, True)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        sel_model = self.table.selectionModel()
        sel_model.selectionChanged.connect(self._table_changed)
        return self.table

    def _init_data(self):
        rows = get_companies()
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                item = QTableWidgetItem(str(v))
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()
        return

    def _txt_read_only(self, value):
        self.txt_rfc.setReadOnly(value)
        self.txt_name.setReadOnly(value)
        self.txt_ciec.setReadOnly(value)
        return

    def _txt_clean(self):
        self.txt_rfc.setText('')
        self.txt_name.setText('')
        self.txt_ciec.setText('')
        self.txt_path.setText('')
        return

    def _new(self):
        self.cmd_new.setEnabled(False)
        self.cmd_save.setEnabled(True)
        self.cmd_edit.setEnabled(False)
        self.cmd_update.setEnabled(False)
        self.cmd_delete.setEnabled(False)
        self.cmd_cancel.setEnabled(True)
        self.cmd_path.setEnabled(True)
        self.cmd_close.setEnabled(False)
        self.table.setEnabled(False)
        self._txt_read_only(False)
        self._txt_clean()
        self.txt_rfc.setFocus()
        return

    def _cancel(self):
        self.cmd_new.setEnabled(True)
        self.cmd_save.setEnabled(False)
        self.cmd_edit.setEnabled(False)
        self.cmd_update.setEnabled(False)
        self.cmd_delete.setEnabled(False)
        self.cmd_cancel.setEnabled(False)
        self.cmd_path.setEnabled(False)
        self.cmd_close.setEnabled(True)
        self.table.setEnabled(True)
        self._txt_read_only(True)
        self._table_changed()
        return

    def _select_path(self):
        path = str(QFileDialog.getExistingDirectory(self, 'Selecciona un directorio'))
        if not os.access(path, os.W_OK):
            msg = 'No tienes derechos de escritura en el directorio seleccionado'
            self._warning(msg)
            return
        self.txt_path.setText(path)
        return

    def _warning(self, msg):
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setWindowTitle(TITLE)
        msgbox.setText(msg)
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.exec()
        return

    def _question(self, msg):
        result = QMessageBox.question(
            self, TITLE, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return result == QMessageBox.Yes

    def _save(self):
        rfc = self.txt_rfc.text().strip().upper()
        if not rfc:
            self.txt_rfc.setFocus()
            msg = 'El campo RFC es requerido'
            self._warning(msg)
            return
        msg = util.validate_rfc(rfc)
        if msg:
            self.txt_rfc.setFocus()
            self._warning(msg)
            return
        name = self.txt_name.text().strip()
        if not name:
            self.txt_name.setFocus()
            msg = 'El campo Razón Social es requerido'
            self._warning(msg)
            return
        ciec = self.txt_ciec.text().strip()
        if not ciec:
            self.txt_ciec.setFocus()
            msg = 'El campo Clave CIEC es requerido'
            self._warning(msg)
            return
        folder = self.txt_path.text().strip()
        if not folder:
            self.cmd_path.setFocus()
            msg = 'El campo Ruta de Descarga es requerido'
            self._warning(msg)
            return

        data = {
            'rfc': rfc,
            'name': name,
            'ciec': ciec,
            'folder': folder,
        }
        msg = save_company(data)
        if msg:
            self._warning(msg)
            return
        self._cancel()
        self._init_data()
        return

    def _table_changed(self):
        self.cmd_delete.setEnabled(True)
        row = self.table.currentRow()
        if row == -1:
            self.cmd_delete.setEnabled(False)
            self._txt_clean()
            return
        self.txt_rfc.setText(self.table.item(row, 1).text())
        self.txt_name.setText(self.table.item(row, 2).text())
        self.txt_path.setText(self.table.item(row, 4).text())
        return

    def _delete(self):
        msg = '¿Estas seguro de eliminar la empresa seleccionada?\n\n' \
            'ESTA ACCIÓN NO SE PUEDE DESHACER'
        if self._question(msg):
            row = self.table.currentRow()
            pk = self.table.item(row, 0).text()
            if delete_company(pk):
                self.table.removeRow(row)
        return

    def _close(self):
        self.done(0)
        return


class AppMain(QMainWindow):

    def __init__(self):
        super().__init__()
        self._msg('Bienvenido...')
        self._init_ui()
        self._init_data()
        now = util.get_now()
        #~ self._get_invoices({'year': now.year, 'month': now.month})
        self._validate_exists_companies()
        self.showMaximized()

    def _init_ui(self):
        self.setWindowTitle(TITLE)
        self.setWindowIcon(QIcon('img/ulm.png'))
        self._menu()
        self.setCentralWidget(TabWidget(self))
        self.txt_uuid.installEventFilter(self)
        self.last_days.installEventFilter(self)
        self.date_start.installEventFilter(self)
        self.date_end.installEventFilter(self)
        self.search_uuid.installEventFilter(self)
        self.search_emisor.installEventFilter(self)
        self.search_receptor.installEventFilter(self)
        self.filter_date_start.installEventFilter(self)
        self.filter_date_end.installEventFilter(self)
        self.txt_path_source_rename.installEventFilter(self)
        self.txt_template_fields.installEventFilter(self)
        self.cbo_template_name.installEventFilter(self)
        self._clip = QApplication.clipboard()
        #~ self._center()
        self._connect()
        return

    def _connect(self):
        self.table_companies_rename.itemClicked.connect(self._table_companies_rename_click)
        self.cmd_path_source_rename.clicked.connect(self._cmd_path_source_rename)
        self.cmd_rename.clicked.connect(self._cmd_rename)
        self.cmd_template_save.clicked.connect(self._cmd_template_save)
        self.cmd_template_delete.clicked.connect(self._cmd_template_delete)
        self.cbo_template_name.currentIndexChanged.connect(self._cbo_template_name_changed)
        return

    #~ def _center(self):
        #~ qr = self.frameGeometry()
        #~ cp = QDesktopWidget().availableGeometry().center()
        #~ qr.moveCenter(cp)
        #~ self.move(qr.topLeft())
        #~ return

    def _init_data(self):
        rows = get_companies()
        self.table_companies.setRowCount(len(rows))
        self.table_companies_rename.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                item = QTableWidgetItem(str(v))
                item2 = QTableWidgetItem(str(v))
                self.table_companies.setItem(r, c, item)
                self.table_companies_rename.setItem(r, c, item2)
        self.table_companies.horizontalHeader().setStretchLastSection(True)
        self.table_companies_rename.horizontalHeader().setStretchLastSection(True)
        self._set_defaul_opt()

        self.templates = db.get_templates()
        rows = sorted(tuple(self.templates.keys()))
        if rows:
            self.cbo_template_name.addItems(rows)
            self.txt_template_fields.setText(self.templates[rows[0]])
        return

    def _get_invoices(self, filters={}):
        rows = get_invoices(filters)
        self.table_invoices.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                if c == 9:
                    if v is None:
                        item = QTableWidgetItem('')
                    else:
                        item = QTableWidgetItem(str(v))
                elif c == 10:
                    item = QTableWidgetItem('$ {0:,.2f}'.format(v))
                else:
                    item = QTableWidgetItem(str(v))
                self.table_invoices.setItem(r, c, item)
                if c == 8 and v == 'Cancelado':
                    self.table_invoices.item(r, c).setBackground(Qt.red)
                elif c == 10:
                    self.table_invoices.item(r, c).setTextAlignment(Qt.AlignRight)
        self.table_invoices.resizeColumnsToContents()
        #~ self.table_invoices.setColumnWidth(1, 50)
        self.table_invoices.setColumnWidth(3, 200)
        self.table_invoices.setColumnWidth(5, 200)
        return

    def _set_defaul_opt(self):
        n = util.get_now()
        self._opt = {
            'sin_descargar': False,
            'tipo_complemento': '-1',
            'tipo': 't',
            'fecha_final': None,
            'fecha_inicial': None,
            'intervalo_dias': None,
            'dia': 0,
            'mes': n.month,
            'año': n.year,
            'uuid': None,
            'folder': '',
            'ciec': '',
            'rfc': ''
        }
        return

    def _validate_exists_companies(self):
        value = bool(self.table_companies.rowCount())
        self.cmd_down_by_date.setEnabled(value)
        self.cmd_down_by_dates.setEnabled(value)
        self.cmd_down_by_days.setEnabled(value)
        self.cmd_down_by_uuid.setEnabled(value)
        if value:
            msg = 'Selecciona al menos una empresa'
        else:
            msg = 'Agrega una empresa para poder descargar'
        self._msg(msg)
        return

    def _menu(self):
        menu = self.menuBar()
        menu_file = menu.addMenu('Archivo')
        menu_help = menu.addMenu('Ayuda')

        cmd_exit = QAction(QIcon('img/close.png'), 'Salir', self)
        cmd_exit.setShortcut('Alt+F4')
        cmd_exit.setStatusTip('Salir de la aplicación (Alt+F4)')
        cmd_exit.triggered.connect(self.close)

        cmd_company = QAction(QIcon('img/companies.png'), 'Empresas', self)
        cmd_company.setShortcut('F2')
        cmd_company.setStatusTip('Administrar empresas (F2)')
        cmd_company.triggered.connect(self._companies)

        self.toolbar = self.addToolBar('Main')
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.addAction(cmd_company)
        self.toolbar.addAction(cmd_exit)

        menu_file.addAction(cmd_company)
        menu_file.addAction(cmd_exit)

        go_url = QAction(QIcon('img/ulm.png'), 'Nuestro Sitio Web', self)
        go_url.setStatusTip('Ir a nuestro sitio web...')
        go_url.triggered.connect(self._go_website)
        go_donate = QAction('Donar...', self)
        go_donate.triggered.connect(self._go_donate)
        go_forum = QAction('Foro de Soporte', self)
        go_forum.triggered.connect(self._go_forum)

        cmd_about = QAction('Acerca de...', self)
        cmd_about.triggered.connect(self._about)

        menu_help.addAction(go_url)
        menu_help.addAction(go_donate)
        menu_help.addAction(go_forum)
        menu_help.addAction(cmd_about)

        return

    def _msg(self, msg):
        self.statusBar().showMessage(msg)
        return

    def _about(self):
        return

    def _go_website(self):
        url = QUrl(WEBSITE)
        QDesktopServices.openUrl(url)
        return

    def _go_donate(self):
        url = QUrl(W_DONATE)
        QDesktopServices.openUrl(url)
        return

    def _go_forum(self):
        url = QUrl(W_FORUM)
        QDesktopServices.openUrl(url)
        return

    def _companies(self):
        dlg = DlgCompanies()
        self._init_data()
        self._validate_exists_companies()
        return

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            color = obj.metaObject().className() + YELLOW
            obj.setStyleSheet(color);
        elif event.type() == QEvent.FocusOut:
            color = obj.metaObject().className() + WHITE
            obj.setStyleSheet(color);
        return False

    def _set_opt(self):
        opt = self.options_types.checkedButton()
        self._opt['tipo'] = opt.text()[0].lower()
        opt = self.options_docs.checkedButton()
        self._opt['tipo_complemento'] = TYPE_CFDI[opt.text()]
        self._opt['sin_subdirectorios'] = False
        return

    def _get_companies(self):
        indexes = self.table_companies.selectedIndexes()
        if not indexes:
            msg = 'Selecciona al menos una empresa'
            warning(msg)
            return False
        return indexes

    def _cmd_down_by_date(self):
        indexes = self._get_companies()
        if not indexes:
            return

        data = []
        self._set_opt()
        self._opt['dia'] = int(self.cbo_day.currentText())
        self._opt['mes'] = self.cbo_month.currentIndex() + 1
        self._opt['año'] = int(self.cbo_year.currentText())
        if self._opt['dia']:
            result = util.validate_date(
                self._opt['año'], self._opt['mes'], self._opt['dia'])
            if isinstance(result, str):
                warning(result)
                return

        for i in indexes:
            row = self._opt.copy()
            row['rfc'] = self.table_companies.item(i.row(), 1).text()
            row['ciec'] = util.get_ciec(self.table_companies.item(i.row(), 3).text())
            row['folder'] = self.table_companies.item(i.row(), 4).text()
            data.append(row)
        self._download(data)
        return

    def _cmd_down_by_dates(self):
        indexes = self._get_companies()
        if not indexes:
            return

        data = []
        self._set_opt()
        self._opt['fecha_inicial'] = util.get_datetime(self.date_start.date().toPyDate())
        self._opt['fecha_final'] = util.get_datetime(self.date_end.date().toPyDate())
        if self._opt['fecha_final'] < self._opt['fecha_inicial']:
            self._opt['fecha_inicial'], self._opt['fecha_final'] = \
                self._opt['fecha_final'], self._opt['fecha_inicial']

        for i in indexes:
            row = self._opt.copy()
            row['rfc'] = self.table_companies.item(i.row(), 1).text()
            row['ciec'] = util.get_ciec(self.table_companies.item(i.row(), 3).text())
            row['folder'] = self.table_companies.item(i.row(), 4).text()
            data.append(row)
        self._download(data)
        return

    def _cmd_down_by_days(self):
        indexes = self._get_companies()
        if not indexes:
            return

        data = []
        self._set_opt()
        self._opt['intervalo_dias'] = self.last_days.value()

        for i in indexes:
            row = self._opt.copy()
            row['rfc'] = self.table_companies.item(i.row(), 1).text()
            row['ciec'] = util.get_ciec(self.table_companies.item(i.row(), 3).text())
            row['folder'] = self.table_companies.item(i.row(), 4).text()
            data.append(row)
        self._download(data)
        return

    def _cmd_down_by_uuid(self):
        indexes = self._get_companies()
        if not indexes:
            return
        if len(indexes) > 1:
            msg = 'Selecciona solo una empresa'
            warning(msg)
            return

        data = []
        self._set_opt()
        self._opt['uuid'] = self.txt_uuid.text().strip()
        if not self._opt['uuid']:
            self.txt_uuid.setFocus()
            msg = 'Captura el UUID a buscar'
            warning(msg)
            return

        if not util.validate_uuid(self._opt['uuid']):
            self.txt_uuid.setFocus()
            msg = 'Captura un UUID valido'
            warning(msg)
            return

        for i in indexes:
            row = self._opt.copy()
            row['rfc'] = self.table_companies.item(i.row(), 1).text()
            row['ciec'] = util.get_ciec(self.table_companies.item(i.row(), 3).text())
            row['folder'] = self.table_companies.item(i.row(), 4).text()
            data.append(row)
        self._download(data)
        return

    def _download(self, data):
        for row in data:
            self._msg('Descargando documentos de: {}'.format(row['rfc']))
            util.sat_download(False, **row)
        self._set_defaul_opt()
        self._msg('Descarga terminada...')
        return

    def _search_uuid(self):
        self._cmd_filter()
        return

    def _search_emisor(self):
        self._cmd_filter()
        return

    def _search_receptor(self):
        self._cmd_filter()
        return

    def _cbo_type(self, text):
        if text == 'Todos':
            text = ''
        self._cmd_filter(type_doc=text)
        return

    def _cbo_status(self, text):
        if text == 'Todos':
            text = ''
        self._cmd_filter(status=text)
        return

    def _cbo_filter_year(self, text):
        if text == 'Todos':
            text = 0
        type_doc = self.cbo_type.currentText()
        if type_doc == 'Todos':
            type_doc = ''
        status = self.cbo_status.currentText()
        if status == 'Todos':
            status = ''
        month = self.cbo_filter_month.currentIndex()

        self._cmd_filter(type_doc=type_doc, status=status, year=int(text), month=month)
        return

    def _cbo_filter_month(self, value):
        year = self.cbo_filter_year.currentText()
        if year == 'Todos':
            year = 0
        type_doc = self.cbo_type.currentText()
        if type_doc == 'Todos':
            type_doc = ''
        status = self.cbo_status.currentText()
        if status == 'Todos':
            status = ''

        self._cmd_filter(type_doc=type_doc, status=status, year=int(year), month=value)
        return

    def _filter_date_start(self):
        self._filter_dates()
        return

    def _filter_date_end(self):
        self._filter_dates()
        return

    def _filter_dates(self):
        date_start = util.get_datetime(self.filter_date_start.date().toPyDate())
        date_end = util.get_datetime(self.filter_date_end.date().toPyDate())
        if date_end < date_start:
            date_start, date_end = date_end, date_start
            date_end = util.add_days(date_end, 1)
        self._cmd_filter(date_start=date_start, date_end=date_end)
        return

    def _cmd_filter(self, type_doc='', status='', year=0, month=0,
        date_start=False, date_end=False):
        filters  = {}
        uuid = self.search_uuid.text().strip()
        if uuid:
            filters['uuid'] = uuid
        emisor = self.search_emisor.text().strip()
        if emisor:
            filters['emisor'] = emisor
        receptor = self.search_receptor.text().strip()
        if receptor:
            filters['receptor'] = receptor
        if type_doc:
            filters['type_doc'] = type_doc
        if status:
            filters['status'] = status
        if year:
            filters['year'] = year
        if month:
            filters['month'] = month
        if date_start:
            filters['start'] = date_start
            filters['end'] = date_end

        self._get_invoices(filters)
        return

    def _tab_changed(self, index):
        if index == 1:
            self.cbo_filter_year.clear()
            #~ self.cbo_filter_month.clear()
            self.cbo_filter_year.addItems(get_years())
            #~ self.cbo_filter_month.addItems(get_months())
            self.cbo_filter_year.setCurrentIndex(self.cbo_filter_year.count() - 1)
            self.cbo_filter_month.setCurrentIndex(util.get_month())

            year = self.cbo_filter_year.currentText()
            if year == 'Todos':
                year = 0
            month = self.cbo_filter_month.currentIndex()
            self._cmd_filter(year=int(year), month=month)
        return

    def _chk_all(self, state):
        if state:
            self.table_invoices.selectAll()
        else:
            self.table_invoices.clearSelection()
        return

    def _cmd_update_sat(self):
        rows = self.table_invoices.selectionModel().selectedRows()
        if not rows:
            msg = 'Selecciona al menos un registro'
            warning(msg)
            return

        cancel = []
        for row in sorted(rows):
            r = row.row()
            total = self.table_invoices.item(r, 10).text()[2:].replace(',', '')
            data = {
                'uuid': self.table_invoices.item(r, 1).text(),
                'emisor_rfc': self.table_invoices.item(r, 4).text(),
                'receptor_rfc': self.table_invoices.item(r, 6).text(),
                'total': total,
            }
            msg = 'Verificando estatus del UUID: {}'.format(data['uuid'])
            self._msg(msg)
            old_status = self.table_invoices.item(r, 8).text()
            new_status = util.get_status_sat(data)
            if old_status != new_status:
                pk = self.table_invoices.item(r, 0).text()
                if update_status(pk, new_status):
                    self.table_invoices.item(r, 8).setText(new_status)
                    if new_status == 'Cancelado':
                        cancel.append(data['uuid'])
        msg = 'Estatus actualizados'
        self._msg(msg)

        if cancel:
            msg = 'IMPORTANTE: Los siguientes documentos han sido ' \
                'cancelados:\n\n{}'.format('\n'.join(cancel))
            warning(msg)
        return

    def _cell_click(self, cell):
        col = cell.column()
        value = cell.text()
        if col in (3,4):
            self.search_emisor.blockSignals(True)
            self.search_emisor.setText(value)
            self.search_emisor.blockSignals(False)
        elif col in (5, 6):
            self.search_receptor.blockSignals(True)
            self.search_receptor.setText(value)
            self.search_receptor.blockSignals(False)
        self._clip.setText(value)
        msg = '{} de {} facturas seleccionadas'.format(
            len(self.table_invoices.selectionModel().selectedRows()),
            self.table_invoices.rowCount())
        self._msg(msg)
        return

    def _table_companies_rename_click(self, cell):
        path = self.table_companies_rename.item(cell.row(), 4).text()
        self.txt_path_source_rename.setText(path)
        self.txt_path_source_rename.setReadOnly(False)
        self.txt_template_fields.setReadOnly(False)
        self.cbo_template_name.setEnabled(True)
        self.cmd_path_source_rename.setEnabled(True)
        self.cmd_rename.setEnabled(True)
        self.cmd_template_save.setEnabled(True)
        self.cmd_template_delete.setEnabled(True)
        self.txt_path_source_rename.setFocus()
        return

    def _cmd_path_source_rename(self):
        path = str(QFileDialog.getExistingDirectory(self, 'Selecciona un directorio'))
        if path and validate_write(path):
            self.txt_path_source_rename.setText(path)
        return

    def _cmd_template_save(self):
        name = self.cbo_template_name.currentText().strip()
        if not validate_text(name):
            self.cbo_template_name.setFocus()
            return
        fields = self.txt_template_fields.text().strip()
        if not validate_text(fields):
            self.txt_template_fields.setFocus()
            return
        msg = db.save_template(name, fields)
        if msg:
            warning(msg)
            self.cbo_template_name.setFocus()
        else:
            self.templates = db.get_templates()
            rows = sorted(tuple(self.templates.keys()))
            if rows:
                self.cbo_template_name.clear()
                self.cbo_template_name.addItems(rows)
                self.cbo_template_name.setEditText(name)
            msg = 'Plantilla guardada correctamente'
            msgbox(msg)
        return

    def _cmd_template_delete(self):
        name = self.cbo_template_name.currentText().strip()
        if not validate_text(name):
            self.cbo_template_name.setFocus()
            return
        msg = '¿Estás seguro de eliminar la plantilla seleccionada?\n\n' \
            'ESTA ACCIÓN NO SE PUEDE DESHACER'
        if not question(msg):
            return

        if db.delete_template(name):
            self.cbo_template_name.removeItem(
                self.cbo_template_name.currentIndex())
            self.cbo_template_name.setEditText('')
            del self.templates[name]
            self.cbo_template_name.setFocus()
            msg = 'Plantilla eliminada correctamente'
            msgbox(msg)
        return

    def _cbo_template_name_changed(self, index):
        fields = self.templates.get(self.cbo_template_name.currentText(), '')
        self.txt_template_fields.setText(fields)
        return

    def _cmd_rename(self):
        path = self.txt_path_source_rename.text().strip()
        if not validate_write(path):
            self.txt_path_source_rename.setFocus()
            return

        template = self.txt_template_fields.text().strip()
        if not validate_text(template):
            self.txt_template_fields.setFocus()
            return

        files = util.get_files(path)
        msg = 'Se encontraron: {} documentos a renombrar.\n\n' \
            '¿Estás seguro de continuar?'.format(len(files))
        if not question(msg):
            return

        i = 0
        for path in files:
            ok, name = util.get_name(path, template)
            if not ok:
                print ('Error en: {}'.format(name))
                continue
            if util.file_rename(path, name):
                i += 1

        msg = 'Documentos encontrados: {}\n'.format(len(files))
        msg += 'Documentos renombrados: {}'.format(i)
        msgbox(msg)
        return

    def _cmd_copy_row(self):
        rows = self.table_invoices.selectionModel().selectedRows()
        if not rows:
            msg = 'Selecciona al menos un registro'
            warning(msg)
            return

        headers = ('id', 'UUID', 'Fecha', 'Emisor', 'RFC Emisor', 'Receptor',
            'RFC Receptor', 'Tipo', 'Estatus SAT', 'Fecha Cancelación', 'Total')
        values = ['\t'.join(headers)]
        cc = range(self.table_invoices.columnCount())
        for row in sorted(rows):
            r = row.row()
            value = '\t'.join([self.table_invoices.item(r, c).text()
                if self.table_invoices.item(r, c) else '' for c in cc])
            values.append(value)
        values = '\n'.join(values)
        self._clip.setText(values)
        return

    def _cmd_delete(self):
        rows = self.table_invoices.selectionModel().selectedRows()
        if not rows:
            msg = 'Selecciona al menos un registro'
            warning(msg)
            return

        msg = '¿Estás seguro de eliminar los registros seleccionados?\n\n' \
            'ESTA ACCION NO SE PUEDE DESHACER'
        if question(msg):
            for row in sorted(rows, reverse=True):
                r = row.row()
                pk = self.table_invoices.item(r, 0).text()
                if delete_invoice(pk):
                    self.table_invoices.removeRow(r)
        return


class MyTable(QTableWidget):

    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)
        self.chk_all = QCheckBox(self)
        self.chk_all.stateChanged.connect(parent._chk_all)

    def resizeEvent(self, event=None):
        super().resizeEvent(event)
        self.chk_all.setGeometry(QRect(10, 4, 17, 17))


class TabWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.p = parent
        self._dates = util.get_range_dates()
        self._init_ui()

    def _init_ui(self):
        self._layout = QVBoxLayout()

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab_download = QWidget()
        self.tab_invoices = QWidget()
        self.tab_rename = QWidget()

        # Add tabs
        self.tabs.addTab(self.tab_download, 'Descarga SAT')
        self.tabs.addTab(self.tab_invoices, 'CFDIs (XMLs)')
        self.tabs.addTab(self.tab_rename, 'Renombrar')

        self._make_tab_dowload()
        self._make_tab_invoices()
        self._make_tab_rename()
        self._connect()

        # Add tabs to widget
        self._layout.addWidget(self.tabs)
        self.setLayout(self._layout)
        return

    def _connect(self):
        self.tabs.currentChanged[int].connect(self.p._tab_changed)
        return

    def _make_tab_dowload(self):
        vbl_download = QVBoxLayout(self)
        hbl1 = QHBoxLayout()
        vbl1 = QVBoxLayout()
        self.p.table_companies = self._table_companies()
        vbl1.addWidget(self.p.table_companies)
        vbl2 = QVBoxLayout()

        self.p.options_types = QButtonGroup()
        opt_all = QRadioButton('Todos')
        opt_all.setChecked(True)
        opt_e = QRadioButton('Emitidos')
        opt_r = QRadioButton('Recibidos')
        self.p.options_types.addButton(opt_all)
        self.p.options_types.addButton(opt_e)
        self.p.options_types.addButton(opt_r)

        gb = QGroupBox('Tipo de descarga:')
        layout = QHBoxLayout()
        layout.addWidget(opt_all)
        layout.addWidget(opt_e)
        layout.addWidget(opt_r)
        layout.addStretch(1)
        gb.setLayout(layout)
        vbl2.addWidget(gb)

        self.p.options_docs = QButtonGroup()
        opt_all_doc = QRadioButton('Todos')
        opt_all_doc.setChecked(True)
        opt_standar = QRadioButton('Estandar')
        opt_nomina11 = QRadioButton('Nómina 1.1')
        opt_nomina12 = QRadioButton('Nómina 1.2')
        self.p.options_docs.addButton(opt_all_doc)
        self.p.options_docs.addButton(opt_standar)
        self.p.options_docs.addButton(opt_nomina11)
        self.p.options_docs.addButton(opt_nomina12)

        gb = QGroupBox('Tipo de documento:')
        layout = QHBoxLayout()
        layout.addWidget(opt_all_doc)
        layout.addWidget(opt_standar)
        layout.addWidget(opt_nomina11)
        layout.addWidget(opt_nomina12)
        layout.addStretch(1)
        gb.setLayout(layout)
        vbl2.addWidget(gb)

        gb = QGroupBox('Descargar por fecha:')
        layout = QHBoxLayout()
        lbl_year = QLabel('Año:')
        lbl_month = QLabel('Mes:')
        lbl_day = QLabel('Día:')
        self.p.cbo_year = QComboBox()
        self.p.cbo_month = QComboBox()
        self.p.cbo_day = QComboBox()
        self.p.cbo_year.addItems(util.get_years())
        self.p.cbo_year.setCurrentIndex(self.p.cbo_year.count() - 1)
        self.p.cbo_month.addItems(util.get_months())
        self.p.cbo_month.setCurrentIndex(util.get_month() - 1)
        self.p.cbo_day.addItems(tuple(map(str, range(32))))
        layout.addWidget(lbl_year)
        layout.addWidget(self.p.cbo_year)
        layout.addWidget(lbl_month)
        layout.addWidget(self.p.cbo_month)
        layout.addWidget(lbl_day)
        layout.addWidget(self.p.cbo_day)
        self.p.cmd_down_by_date = QPushButton('Descargar')
        self.p.cmd_down_by_date.clicked.connect(self.p._cmd_down_by_date)
        layout.addStretch(1)
        layout.addWidget(self.p.cmd_down_by_date)
        gb.setLayout(layout)
        vbl2.addWidget(gb)

        gb = QGroupBox('Descargar por rango de fechas:')
        layout = QHBoxLayout()
        lbl_date_start = QLabel('Desde:')
        lbl_date_start.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_date_end = QLabel('Hasta:')
        lbl_date_end.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.p.date_start = QDateEdit()
        self.p.date_start.setDateRange(*self._dates)
        self.p.date_start.setDateTime(util.get_first_day())
        self.p.date_start.setCalendarPopup(True)
        self.p.date_start.setDisplayFormat('dd-MMM-yyyy')
        self.p.date_end = QDateEdit()
        self.p.date_end.setDateRange(*self._dates)
        self.p.date_end.setDateTime(self._dates[1])
        self.p.date_end.setCalendarPopup(True)
        self.p.date_end.setDisplayFormat('dd-MMM-yyyy')
        layout.addWidget(lbl_date_start)
        layout.addWidget(self.p.date_start)
        layout.addWidget(lbl_date_end)
        layout.addWidget(self.p.date_end)
        self.p.cmd_down_by_dates = QPushButton('Descargar')
        self.p.cmd_down_by_dates.clicked.connect(self.p._cmd_down_by_dates)
        layout.addStretch(1)
        layout.addWidget(self.p.cmd_down_by_dates)
        gb.setLayout(layout)
        vbl2.addWidget(gb)

        gb = QGroupBox('Descargar por:')
        lbl_last_days = QLabel('Ultimos:')
        lbl_last_days.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_days = QLabel('días')
        self.p.last_days = QSpinBox()
        self.p.last_days.setRange(1, 30)
        self.p.last_days.setValue(5)
        layout = QHBoxLayout()
        layout.addWidget(lbl_last_days)
        layout.addWidget(self.p.last_days)
        layout.addWidget(lbl_days)
        self.p.cmd_down_by_days = QPushButton('Descargar')
        self.p.cmd_down_by_days.clicked.connect(self.p._cmd_down_by_days)
        layout.addStretch(1)
        layout.addWidget(self.p.cmd_down_by_days)
        gb.setLayout(layout)
        vbl2.addWidget(gb)

        gb = QGroupBox('Descargar por:')
        lbl_uuid = QLabel('UUID:')
        lbl_uuid.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.p.txt_uuid = QLineEdit()
        layout = QHBoxLayout()
        layout.addWidget(lbl_uuid)
        layout.addWidget(self.p.txt_uuid)
        self.p.cmd_down_by_uuid = QPushButton('Descargar')
        self.p.cmd_down_by_uuid.clicked.connect(self.p._cmd_down_by_uuid)
        layout.addWidget(self.p.cmd_down_by_uuid)
        gb.setLayout(layout)
        vbl2.addWidget(gb)

        vbl2.addStretch(1)

        hbl1.addLayout(vbl1)
        hbl1.addLayout(vbl2)
        hbl1.addStretch(1)
        vbl_download.addLayout(hbl1)

        self.tab_download.setLayout(vbl_download)
        return

    def _make_tab_invoices(self):
        vbl_download = QVBoxLayout(self)
        #~ Toolbar
        layout = QHBoxLayout()
        self.p.cmd_copy_row = QPushButton('')
        icon = QIcon('img/row.png')
        self.p.cmd_copy_row.setIcon(icon)
        self.p.cmd_delete = QPushButton('Eliminar')
        self.p.cmd_update_sat = QPushButton('Actualizar Estatus SAT')
        self.p.cmd_copy_row.clicked.connect(self.p._cmd_copy_row)
        self.p.cmd_delete.clicked.connect(self.p._cmd_delete)
        self.p.cmd_update_sat.clicked.connect(self.p._cmd_update_sat)

        layout.addWidget(self.p.cmd_copy_row)
        layout.addStretch(1)
        layout.addWidget(self.p.cmd_update_sat)
        layout.addWidget(self.p.cmd_delete)
        vbl_download.addLayout(layout)
        #~ Filters
        layout = QHBoxLayout()
        lbl_uuid = QLabel('UUID:')
        lbl_emisor = QLabel('Emisor:')
        lbl_receptor = QLabel('Receptor:')
        lbl_type = QLabel('Tipo:')
        lbl_status = QLabel('Estatus SAT:')
        lbl_uuid.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_emisor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_receptor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_type.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.p.search_uuid = QLineEdit()
        self.p.search_emisor = QLineEdit()
        self.p.search_receptor = QLineEdit()
        self.p.cbo_type = QComboBox()
        self.p.cbo_status = QComboBox()
        self.p.cbo_type.addItems(('Todos', 'ingreso', 'egreso', 'traslado'))
        self.p.cbo_status.addItems(('Todos', 'Vigente', 'Cancelado'))

        self.p.search_uuid.textChanged.connect(self.p._search_uuid)
        self.p.search_emisor.textChanged.connect(self.p._search_emisor)
        self.p.search_receptor.textChanged.connect(self.p._search_receptor)
        self.p.cbo_type.activated[str].connect(self.p._cbo_type)
        self.p.cbo_status.activated[str].connect(self.p._cbo_status)

        self.p.cmd_filter = QPushButton('Filtrar')
        self.p.cmd_filter.clicked.connect(self.p._cmd_filter)

        layout.addWidget(lbl_uuid)
        layout.addWidget(self.p.search_uuid)
        layout.addWidget(lbl_emisor)
        layout.addWidget(self.p.search_emisor)
        layout.addWidget(lbl_receptor)
        layout.addWidget(self.p.search_receptor)
        layout.addWidget(lbl_type)
        layout.addWidget(self.p.cbo_type)
        layout.addWidget(lbl_status)
        layout.addWidget(self.p.cbo_status)
        layout.addWidget(self.p.cmd_filter)
        vbl_download.addLayout(layout)

        lbl_filter_year = QLabel('Año:')
        lbl_filter_month = QLabel('Mes:')
        self.p.cbo_filter_year = QComboBox()
        self.p.cbo_filter_month = QComboBox()
        self.p.cbo_filter_month.addItems(('Todos',) + util.get_months())
        lbl_filter_date_start = QLabel('Desde:')
        lbl_filter_date_end = QLabel('Hasta:')
        lbl_filter_year.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_filter_month.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_filter_date_start.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_filter_date_end.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.p.filter_date_start = QDateEdit()
        self.p.filter_date_start.setDateRange(*self._dates)
        self.p.filter_date_start.setDateTime(util.get_first_day())
        self.p.filter_date_start.setCalendarPopup(True)
        self.p.filter_date_start.setDisplayFormat('dd-MMM-yyyy')
        self.p.filter_date_end = QDateEdit()
        self.p.filter_date_end.setDateRange(*self._dates)
        self.p.filter_date_end.setDateTime(self._dates[1])
        self.p.filter_date_end.setCalendarPopup(True)
        self.p.filter_date_end.setDisplayFormat('dd-MMM-yyyy')

        layout = QHBoxLayout()
        layout.addWidget(lbl_filter_year)
        layout.addWidget(self.p.cbo_filter_year)
        layout.addWidget(lbl_filter_month)
        layout.addWidget(self.p.cbo_filter_month)
        layout.addWidget(lbl_filter_date_start)
        layout.addWidget(self.p.filter_date_start)
        layout.addWidget(lbl_filter_date_end)
        layout.addWidget(self.p.filter_date_end)
        layout.addStretch(1)
        vbl_download.addLayout(layout)

        self.p.cbo_filter_year.activated[str].connect(self.p._cbo_filter_year)
        self.p.cbo_filter_month.activated[int].connect(self.p._cbo_filter_month)
        self.p.filter_date_start.dateChanged.connect(self.p._filter_date_start)
        self.p.filter_date_end.dateChanged.connect(self.p._filter_date_end)

        self.p.table_invoices = self._table_invoices()
        self.p.table_invoices.itemClicked.connect(self.p._cell_click)
        vbl_download.addWidget(self.p.table_invoices)
        self.tab_invoices.setLayout(vbl_download)
        return

    def _make_tab_rename(self):
        vbl_rename = QVBoxLayout(self)
        hbl = QHBoxLayout()

        layout = QVBoxLayout()
        self._table_companies_for_rename()
        layout.addWidget(self.p.table_companies_rename)
        hbl.addLayout(layout)

        layout = QVBoxLayout()
        lbl_path_source_rename = QLabel('Ruta origen de CFDIs (XMLs):')

        hl = QHBoxLayout()
        self.p.txt_path_source_rename = QLineEdit()
        self.p.txt_path_source_rename.setMinimumWidth(500)
        self.p.txt_path_source_rename.setReadOnly(True)
        self.p.cmd_path_source_rename = QPushButton('Examinar...')
        self.p.cmd_path_source_rename.setEnabled(False)
        hl.addWidget(self.p.txt_path_source_rename)
        hl.addWidget(self.p.cmd_path_source_rename)
        layout.addWidget(lbl_path_source_rename)
        layout.addLayout(hl)

        lbl_template_name = QLabel('Nombre de la plantilla:')
        hl = QHBoxLayout()
        self.p.cbo_template_name = QComboBox()
        self.p.cbo_template_name.setEditable(True)
        self.p.cbo_template_name.setEnabled(False)
        self.p.cmd_template_save = QPushButton('Guardar')
        self.p.cmd_template_delete = QPushButton('Eliminar')
        self.p.cmd_template_save.setMaximumWidth(100)
        self.p.cmd_template_delete.setMaximumWidth(100)
        self.p.cmd_template_save.setEnabled(False)
        self.p.cmd_template_delete.setEnabled(False)
        hl.addWidget(self.p.cbo_template_name)
        hl.addWidget(self.p.cmd_template_save)
        hl.addWidget(self.p.cmd_template_delete)
        layout.addWidget(lbl_template_name)
        layout.addLayout(hl)

        lbl_template_fields = QLabel('Campos de la plantilla:')
        hl = QHBoxLayout()
        self.p.txt_template_fields = QLineEdit()
        self.p.txt_template_fields.setMinimumWidth(500)
        self.p.txt_template_fields.setReadOnly(True)
        self.p.cmd_rename = QPushButton('Renombrar')
        self.p.cmd_rename.setEnabled(False)
        hl.addWidget(self.p.txt_template_fields)
        hl.addWidget(self.p.cmd_rename)
        layout.addWidget(lbl_template_fields)
        layout.addLayout(hl)

        layout.addStretch(1)
        hbl.addLayout(layout)

        hbl.addStretch(1)
        vbl_rename.addLayout(hbl)
        self.tab_rename.setLayout(vbl_rename)
        return

    def _table_companies(self):
        headers = ('id', 'RFC', 'Razón Social', 'CIEC', 'Ruta')
        table_companies = QTableWidget()
        table_companies.setMinimumWidth(300)
        table_companies.horizontalHeader().setStretchLastSection(True)
        table_companies.setColumnCount(5)
        table_companies.setColumnHidden(0, True)
        table_companies.setColumnHidden(1, True)
        table_companies.setColumnHidden(3, True)
        table_companies.setColumnHidden(4, True)
        table_companies.setHorizontalHeaderLabels(headers)
        table_companies.setSelectionMode(QAbstractItemView.MultiSelection)
        table_companies.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_companies.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return table_companies

    def _table_companies_for_rename(self):
        headers = ('id', 'RFC', 'Razón Social', 'CIEC', 'Ruta')
        table = QTableWidget()
        table.setMinimumWidth(300)
        table.horizontalHeader().setStretchLastSection(True)
        table.setColumnCount(5)
        table.setColumnHidden(0, True)
        table.setColumnHidden(1, True)
        table.setColumnHidden(3, True)
        table.setColumnHidden(4, True)
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.p.table_companies_rename = table
        return

    def _table_invoices(self):
        headers = ('id', 'UUID', 'Fecha', 'Emisor', 'RFC Emisor', 'Receptor',
            'RFC Receptor', 'Tipo', 'Estatus SAT', 'Fecha Cancelación', 'Total',
            'Acciones')
        table = MyTable(self.p)
        table.setMinimumWidth(500)
        table.horizontalHeader().setStretchLastSection(True)
        table.setCornerButtonEnabled(False)
        table.setColumnCount(12)
        table.setColumnHidden(0, True)
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionMode(QAbstractItemView.MultiSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        #~ table.setSortingEnabled(True)
        return table


def main():
    create_tables()
    qapp = QApplication(sys.argv)
    pixmap = QPixmap("img/logo.png")
    splash = QSplashScreen(pixmap)
    app = AppMain()
    splash.show()
    sys.exit(qapp.exec_())
    return


if __name__ == '__main__':
    main()

