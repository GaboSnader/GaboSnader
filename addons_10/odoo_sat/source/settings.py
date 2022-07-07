#!/usr/bin/env python

import sys
import logbook
from logbook import Logger, StreamHandler, RotatingFileHandler
logbook.set_datetime_format("local")

from conf import DB, DEBUG

#~ Si es False, solo muestra los mensajes INFO
#~ DEBUG = True

DB = DB
#~ Establece la ruta al archivo LOG de registros
LOG_PATH = 'cfdi.log'
LOG_NAME = 'CFDI'
LOG_LEVEL = 'INFO'


format_string = '[{record.time:%d-%b-%Y %H:%M:%S}] ' \
    '{record.level_name}: ' \
    '{record.channel}: ' \
    '{record.message}'
RotatingFileHandler(
    LOG_PATH,
    backup_count=10,
    max_size=1073741824,
    level=LOG_LEVEL,
    format_string=format_string).push_application()

if DEBUG:
    LOG_LEVEL = 'DEBUG'

StreamHandler(
    sys.stdout,
    level=LOG_LEVEL,
    format_string=format_string).push_application()

log = Logger(LOG_NAME)

#~ Aumenta el tiempo (segundos) de espera, solo si tienes una conexión muy lenta o inestable
TIMEOUT = 10

#~ Cantidad de veces que se intenta en:
#~ - Identificarse en el SAT
#~ - Descargar un CFDI si hay timeout
#~ - Descargar faltantes de la lista obtenida al buscar
TRY_COUNT = 3

#~ Ruta al ejecutable pdftotext, necesario para extraer la fecha de cancelación
#~ de los documentos emitidos
PDF_TO_TEXT = 'pdftotext'
if 'win' in sys.platform:
    PDF_TO_TEXT = 'pdftotext.exe'

WEBSITE = 'http://universolibre.org'
W_DONATE = 'http://universolibre.org/hacemos'
W_FORUM = 'https://foro.empresalibre.net/'

HEADERS = {'Auth-Token': '', 'content-type': 'application/json'}
base = 'https://api.admincfdi.net/{}'
if DEBUG:
    base = 'http://localhost:8000/{}'
URL = {
    'RESOLVE': base.format('resolveCaptcha'),
}
