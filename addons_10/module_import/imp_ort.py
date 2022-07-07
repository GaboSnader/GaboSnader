# -*- coding: utf-8 -*-
#!/usr/bin/python
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime
from openerp.modules import module
from zipfile import *
from StringIO import StringIO
from os import listdir

import os
import sys

import tempfile
import tarfile
import gzip

import base64

class import_module(models.TransientModel):
    _name = 'import.module'
    _description = 'Importar un Modulo de Formato Zip'

    file = fields.Binary('Archivo')
    datas_fname = fields.Char('Nombre del Archivo',size=256)

    @api.multi
    def module_import(self, file):
        print "################## SELF FILE >>>>>>>>>>>>>>>>>> ", self.file
        if (self.datas_fname.endswith("tar.gz")):
            path_scripts = os.system('find . -name odoo_start.sh')
            print "########### SELF NAME PATH SCRIPT >>>>>>>>>>>>>>> ", path_scripts
            if path_scripts == '/opt/start_odoo.sh':
                context = dict(self._context or {})
                split_name_module = self.datas_fname.split(".tar.gz")
                path_act_module = module.get_module_path('module_import')
                path_complete = path_act_module+'/modules/'
                module_name, des= split_name_module
                path_module = module.get_module_path(module_name)
                if path_module == False:
                    raise ValidationError(_('El Modulo Que Desea Actualizar No Existe'))
                else:
                    split_path_module, com = path_module.split(module_name)
                    path_module = split_path_module+module_name
                    compress_file = open(path_complete+self.datas_fname, "wb")
                    compress_file.write(base64.b64decode(self.file))
                    arch_module = path_complete+self.datas_fname
                    os.system('tar -xvf %s -C %s' % (arch_module,path_complete))
                    descom_module = path_complete+module_name
                    cont_listdir = len(listdir(descom_module))
                    if cont_listdir == 1:
                        raise ValidationError(_('Error Al Descomprimir El Modulo'))
                        os.system('rm -R %s && %s' %(arch_module,descom_module))
                    else:
                        os.system('rm -R %s' %(path_module))
                        os.system('mv %s %s' %(descom_module,split_path_module))
                        os.system('rm -R %s && %s' %(arch_module,descom_module))
                        os.system('screen /opt/odoo_start.sh')            
            else:
                raise ValidationError(_('No Se Puede Reiniciar'))
        else:
            raise ValidationError(_('El Archivo Debe Ser Formato "tar.gz"'))



