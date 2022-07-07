# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://www.hesatecnica.com.com/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@hesatecnica.com)
############################################################################
#    Coded by: german_442 email: (german.ponce@hesatecnica.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Ventas Rapidas de Mostrador',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Sales",
    'description': """
    
VENTAS DE MOTRADOR:
===================
    
    Este modulo permite la posibilidad de Vender de una manera rapida y facil.
        * Captura de Ventas desde lector de Codigo de Barras.
            * Captura del Producto con la Referencia Interna y la posibilidad de añadir la Cantidad deseada ejemplo: RF000+4 al añadir el + y la cantidad automaticamente el Sistema añadira la linea con la cantidad correcta.
            * Añade un Boton con la posibilidad de recalcular la Venta con una nueva Tarifa.
        * En Vista Formulario y Lista podemos visualizar por medio de un campo aquellos Pedidos que fueron Pagados.
        * En la Pantalla de Pagos tenemos una relacion directa con Pedidos de Venta, tanto en el formulario como en la vista de Lista.
        * Asistente que permite Registrar Pagos desde el Pedido de Venta.
        * Imagen del Producto que estamos Vendiendo en el desgloce de la Venta.

    Validaciones:
        * Al Cancelar el Pedido, el sistema revisa si tiene pagos relacionados y estos no debes estar asentados para que puedas cancelar el mismo.
        * Al Conciliar Pagos de Ventas en la Factura, se valida que todo los Pedidos se encuentren Pagados.
        * Entrega de Mercancia de Pedidos:
            * Solo puede entregarse un Albaran si el Pedido esta Pagado.
                * Excepcion: Se puede entregar si se activa el Campo Excepcion de Pago en el Pedido de Venta, este grupo esta limitado solo para los usuarios del Grupo Asesor Contable.
        * Registro de Pagos de Facturas (No Conciliacion), el sistema no permite el registro de nuevos Pagos en Una Factura que proviene de Pedidos Pagados.
            * Para manejar una excepcion, tenemos que crear un Pedido con excepcion de Pago y de esta manera podremos enviar producto sin pago y poder pagar una Factura.
            
    Facturacion:
        * El Modulo Cuenta con un Boton que nos permite Conciliar el Pago del Pedido de Venta con el movimiento contable de la Factura (Boton Conciliar Pagos Ventas).
        * Al Cancelar un Pago de un Pedido, este marca el Pedido como no pagado.

    Reportes:
        * El modulo reemplaza el Boton Imprimir por el Reporte Ticket de Venta.

    """,
    "website" : "http://argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","web_tree_image","l10n_mx_einvoice","argil_pos_invoice"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "sale_view.xml",
                    "report.xml",
                    ],
    "installable" : True,
    "active" : False,
}
