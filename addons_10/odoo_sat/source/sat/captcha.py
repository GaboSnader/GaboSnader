#!/usr/bin/env python

import base64
import requests
from io import BytesIO
try:
    from PIL import Image
except ImportError as e:
    pass

try:
    from PyQt5 import QtWidgets as QTW
    from PyQt5 import QtCore as QTC
    from PyQt5 import QtGui as QTG
except ImportError as e:
    pass

from conf import TOKEN
from settings import (
    log,
    HEADERS,
    TIMEOUT,
    URL,
)


YELLOW = ' { background-color: #FFFACD }'
WHITE = ' { background-color: white }'


class DlgCaptcha(QTW.QDialog):
    TITLE = 'Empresa Libre'
    value = ''

    def __init__(self, captcha):
        super().__init__()
        self._init_ui(captcha)
        self.exec()

    def eventFilter(self, obj, event):
        if event.type() == QTC.QEvent.FocusIn:
            color = obj.metaObject().className() + YELLOW
            obj.setStyleSheet(color);
        elif event.type() == QTC.QEvent.FocusOut:
            color = obj.metaObject().className() + WHITE
            obj.setStyleSheet(color);
        return False

    def _init_ui(self, captcha):
        self.setWindowTitle(self.TITLE)
        self.cmd_send = QTW.QPushButton('Enviar')
        vbox = QTW.QVBoxLayout()

        lbl_captcha = QTW.QLabel(self)
        pixmap = QTG.QPixmap()
        pixmap.loadFromData(captcha)
        lbl_captcha.setPixmap(pixmap)

        lbl_title = QTW.QLabel('Captura el texto del CAPTCHA')
        self.txt_catpcha = QTW.QLineEdit()
        self.txt_catpcha.setMaxLength(20)

        hbox = QTW.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.cmd_send)
        hbox.addStretch(1)

        vbox.addWidget(lbl_captcha)
        vbox.addWidget(lbl_title)
        vbox.addWidget(self.txt_catpcha)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.cmd_send.clicked.connect(self._send)
        self.txt_catpcha.installEventFilter(self)
        self.setFixedSize(250, 200)
        return

    def _warning(self, msg):
        msgbox = QTW.QMessageBox()
        msgbox.setIcon(QTW.QMessageBox.Critical)
        msgbox.setWindowTitle(self.TITLE)
        msgbox.setText(msg)
        msgbox.setStandardButtons(QTW.QMessageBox.Ok)
        msgbox.exec()
        return

    def _send(self):
        self.value = self.txt_catpcha.text().strip()
        if not self.value:
            self.txt_catpcha.setFocus()
            msg = 'El captcha es necesario'
            self._warning(msg)
            return
        self.done(0)
        return


def resolve(captcha, from_script):
    print (captcha)
    img = Image.open(BytesIO(captcha))
    print (img)
    img.save("captcha.PNG")
    if TOKEN:
        msg = 'Enviando a resolver captcha'
        log.info(msg)
        HEADERS['Auth-Token'] = TOKEN
        image = base64.b64encode(captcha).decode('utf-8')
        response = requests.post(URL['RESOLVE'],
            json=image, headers=HEADERS, timeout=60)

        if response is None:
            msg = 'Error al intentar resolver el captcha'
            log.error(msg)
            return ''

        if response.status_code != 200:
            log.error(response.json())
            return ''

        result = response.json()
        if not result['ok']:
            log.error(result['value'])
            return

        return result['value']

    if from_script:
        #im = Image.open(BytesIO(captcha))
        #im.show()
        #im.save("image.PNG")
        return input('Captcha: ')

    dlg = DlgCaptcha(captcha)
    return dlg.value
