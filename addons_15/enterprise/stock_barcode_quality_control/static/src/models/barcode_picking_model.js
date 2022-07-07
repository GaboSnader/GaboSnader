/** @odoo-module **/

import BarcodePickingModel from '@stock_barcode/models/barcode_picking_model';
import { patch } from 'web.utils';

patch(BarcodePickingModel.prototype, 'stock_barcode_quality_control', {
    openQualityChecksMethod: 'check_quality',
});
