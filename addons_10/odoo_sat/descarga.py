# -*- coding: utf-8 -*-
#!/usr/bin/python
from openerp import models, fields, api
from openerp.modules import module
import os, sys
from PIL import Image
import base64


class download_sat(models.Model):
    _name='download.sat'
    _description='Modelo interfaz de descarga'
    captcha=fields.Char('captcha')
    photo = fields.Binary('')

    @api.multi
    def connection(self):
        print "#################con"
        path_module = module.get_module_path('odoo_sat')
        print path_module 
        nameimg ='captcha.PNG'
        path= '/opt/odoo/addons_sat/odoo_sat/source/'
        imagpath = path+nameimg
        imag = Image.open (imagpath,mode='r')
        imag = imag.resize((200, 100), Image.ANTIALIAS)
        imag.show()

        #with open("/opt/odoo/addons_sat/odoo_sat/source/captcha.PNG", "rb") as f:
        #data = f.read()
        #print data.encode("base64")



        

        