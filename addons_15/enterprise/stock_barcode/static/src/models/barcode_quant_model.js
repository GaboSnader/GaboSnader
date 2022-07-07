/** @odoo-module **/

import BarcodeModel from '@stock_barcode/models/barcode_model';
import {_t} from "web.core";
import { sprintf } from '@web/core/utils/strings';

export default class BarcodeQuantModel extends BarcodeModel {
    constructor(params) {
        super(...arguments);
        this.lineModel = params.model;
        this.lineFormViewReference = 'stock_barcode.stock_quant_barcode';
        this.validateMessage = _t("The inventory adjustment has been validated");
        this.validateMethod = 'action_validate';
    }

    setData(data) {
        super.setData(...arguments);
        const companies = data.data.records['res.company'];
        this.companyIds = companies.map(company => company.id);
        this.userId = data.data.user_id;
        // Get back all locations used by the quants to list them.
        this.locationList = [];
        for (const page of this.pages) {
            if (page.lines.length) {
                const locationId = page.lines[0].location_id;
                this.locationList.push(this.cache.getRecord('stock.location', locationId));
            }
        }
    }

    getDisplayIncrementBtn(line) {
        if (line.product_id.tracking === 'serial' && (line.inventory_quantity > 0 || (!line.lot_name && !line.lot_id))) {
            return false;
        } else if (line.product_id.tracking === 'lot' && (!line.lot_name && !line.lot_id)) {
            return false;
        }
        return true;
    }

    getDisplayDecrementBtn(line) {
        return this.getQtyDone(line) > 0;
    }

    getQtyDone(line) {
        return line.inventory_quantity;
    }

    getQtyDemand(line) {
        return line.quantity;
    }

    getActionRefresh(newId) {
        const action = super.getActionRefresh(newId);
        action.params.res_id = this.currentState.lines.map(l => l.id);
        action.params.res_id.push(newId);
        return action;
    }

    get printButtons() {
        return [{
            name: _t("Print Inventory"),
            class: 'o_print_inventory',
            action: 'stock.action_report_inventory',
        }];
    }

    get recordIds() {
        return this.currentState.lines.map(l => l.id);
    }

    updateLineQty(virtualId, qty = 1) {
        this.actionMutex.exec(() => {
            const line = this.pageLines.find(l => l.virtual_id === virtualId);
            this.updateLine(line, {inventory_quantity: qty});
            this.trigger('update');
        });
    }

    // --------------------------------------------------------------------------
    // Private
    // --------------------------------------------------------------------------

    _getNewLineDefaultContext() {
        return {
            default_company_id: this.companyIds[0],
            default_location_id: this.location.id,
            default_inventory_quantity: 1,
            default_user_id: this.userId,
            inventory_mode: true,
        };
    }

    _createCommandVals(line) {
        const values = {
            dummy_id: line.virtual_id,
            inventory_date: new Date(),
            inventory_quantity: line.inventory_quantity,
            location_id: line.location_id,
            lot_id: line.lot_id,
            lot_name: line.lot_name,
            package_id: line.package_id,
            product_id: line.product_id,
            owner_id: line.owner_id,
            user_id: this.userId,
        };
        for (const [key, value] of Object.entries(values)) {
            values[key] = this._fieldToValue(value);
        }
        return values;
    }

    async _createNewLine(params) {
        // When creating a new line, we need to know if a quant already exists
        // for this line, and in this case, update the new line fields.
        const product = params.fieldsParams.product_id;
        const domain = [
            ['location_id', '=', this.location.id],
            ['product_id', '=', product.id],
        ];
        if (product.tracking !== 'none') {
            domain.push(['lot_id.name', '=', params.fieldsParams.lot_name]);
        }
        if (params.fieldsParams.package_id) {
            domain.push(['package_id', '=', params.fieldsParams.package_id]);
        }
        const quantity = await this.orm.searchRead(
            'stock.quant',
            domain,
            ['id', 'quantity'],
            { limit: 1 }
        );
        if (quantity.length) {
            params.fieldsParams = Object.assign(params.fieldsParams, quantity[0]);
        }
        const newLine = await super._createNewLine(params);
        return newLine;
    }

    _convertDataToFieldsParams(args) {
        const params = {
            inventory_quantity: args.qty,
            lot_id: args.lot,
            lot_name: args.lotName,
            owner_id: args.owner,
            package_id: args.package || args.resultPackage,
            product_id: args.product,
            product_uom_id: args.product && args.product.uom_id,
        };
        return params;
    }

    _getNewLineDefaultValues(args) {
        const defaultValues = super._getNewLineDefaultValues();
        return Object.assign(defaultValues, {
            inventory_quantity: 0,
            quantity: 0,
            user_id: this.userId,
        });
    }

    _getFieldToWrite() {
        return [
            'inventory_quantity',
            'user_id',
            'location_id',
            'lot_name',
            'lot_id',
            'package_id',
            'owner_id',
        ];
    }

    _getSaveCommand() {
        const commands = this._getSaveLineCommand();
        if (commands.length) {
            return {
                route: '/stock_barcode/save_barcode_data',
                params: {
                    model: this.params.model,
                    res_id: false,
                    write_field: false,
                    write_vals: commands,
                },
            };
        }
        return {};
    }

    _groupSublines(sublines, ids, virtual_ids, qtyDemand, qtyDone) {
        return Object.assign(super._groupSublines(...arguments), {
            inventory_quantity: qtyDone,
            quantity: qtyDemand,
        });
    }

    _lineIsNotComplete(line) {
        return line.inventory_quantity === 0;
    }

    async _processPackage(barcodeData) {
        const { packageType, packageName } = barcodeData;
        let recPackage = barcodeData.package;
        this.lastScannedPackage = false;
        if (!recPackage && !packageType && !packageName) {
            return; // No Package data to process.
        }
        // Scan a new package and/or a package type -> Create a new package with those parameters.
        const currentLine = this.selectedLine || this.lastScannedLine;
        if (currentLine.package_id && packageType &&
            !recPackage && ! packageName &&
            currentLine.package_id.id !== packageType) {
            // Changes the package type for the scanned one.
            await this.orm.write('stock.quant.package', [currentLine.package_id.id], {
                package_type_id: packageType.id,
            });
            const message = sprintf(
                _t("Package type %s was correctly applied to the package %s"),
                packageType.name, currentLine.package_id.name
            );
            barcodeData.stopped = true;
            return this.notification.add(message, { type: 'success' });
        }
        if (!recPackage) {
            if (currentLine && !currentLine.package_id) {
                const valueList = {};
                if (packageName) {
                    valueList.name = packageName;
                }
                if (packageType) {
                    valueList.package_type_id = packageType.id;
                }
                const newPackageData = await this.orm.call(
                    'stock.quant.package',
                    'action_create_from_barcode',
                    [valueList]
                );
                this.cache.setCache(newPackageData);
                recPackage = newPackageData['stock.quant.package'][0];
            }
        }
        if (!recPackage && packageName) {
            const currentLine = this.selectedLine || this.lastScannedLine;
            if (currentLine && !currentLine.package_id) {
                const newPackageData = await this.orm.call(
                    'stock.quant.package',
                    'action_create_from_barcode',
                    [{ name: packageName }]
                );
                this.cache.setCache(newPackageData);
                recPackage = newPackageData['stock.quant.package'][0];
            }
        }
        if (!recPackage || (
            recPackage.location_id && recPackage.location_id != this.currentLocationId
        )) {
            return;
        }
        // TODO: can check if quants already in cache to avoid to make a RPC if
        // there is all in it (or make the RPC only on missing quants).
        const res = await this.orm.call(
            'stock.quant',
            'get_stock_barcode_data_records',
            [recPackage.quant_ids]
        );
        const quants = res.records['stock.quant'];
        if (!quants.length) { // Empty package => Assigns it to the last scanned line.
            const currentLine = this.selectedLine || this.lastScannedLine;
            if (currentLine && !currentLine.package_id && !currentLine.result_package_id) {
                const fieldsParams = this._convertDataToFieldsParams({
                    resultPackage: recPackage,
                });
                await this.updateLine(currentLine, fieldsParams);
                barcodeData.stopped = true;
                this.selectedLineVirtualId = false;
                this.lastScannedPackage = recPackage.id;
                this.trigger('update');
            }
            return;
        }
        this.cache.setCache(res.records);

        // Checks if the package is already scanned.
        let alreadyExisting = 0;
        for (const line of this.pages[this.pageIndex].lines) {
            if (line.package_id && line.package_id.id === recPackage.id &&
                this.getQtyDone(line) > 0) {
                alreadyExisting++;
            }
        }
        if (alreadyExisting === quants.length) {
            barcodeData.error = _t("This package is already scanned.");
            return;
        }
        // For each quants, creates or increments a barcode line.
        for (const quant of quants) {
            const product = this.cache.getRecord('product.product', quant.product_id);
            const searchLineParams = Object.assign({}, barcodeData, { product });
            const currentLine = this._findLine(searchLineParams);
            if (currentLine) { // Updates an existing line.
                const fieldsParams = this._convertDataToFieldsParams({
                    qty: quant.quantity,
                    lotName: barcodeData.lotName,
                    lot: barcodeData.lot,
                    package: recPackage,
                    owner: barcodeData.owner,
                });
                await this.updateLine(currentLine, fieldsParams);
            } else { // Creates a new line.
                const fieldsParams = this._convertDataToFieldsParams({
                    product,
                    qty: quant.quantity,
                    lot: quant.lot_id,
                    package: quant.package_id,
                    resultPackage: quant.package_id,
                    owner: quant.owner_id,
                });
                await this._createNewLine({ fieldsParams });
            }
        }
        barcodeData.stopped = true;
        this.selectedLineVirtualId = false;
        this.lastScannedPackage = recPackage.id;
        this.trigger('update');
    }

    _updateLineQty(line, args) {
        if (args.quantity) { // Set stock quantity.
            line.quantity = args.quantity;
        }
        if (args.inventory_quantity) { // Increments inventory quantity.
            if (args.uom) {
                // An UoM was passed alongside the quantity, needs to check it's
                // compatible with the product's UoM.
                const productUOM = this.cache.getRecord('uom.uom', line.product_id.uom_id);
                if (args.uom.category_id !== productUOM.category_id) {
                    // Not the same UoM's category -> Can't be converted.
                    const message = sprintf(
                        _t("Scanned quantity uses %s as Unit of Measure, but this UoM is not compatible with the product's one (%s)."),
                        args.uom.name, productUOM.name
                    );
                    return this.notification.add(message, { title: _t("Wrong Unit of Measure"), type: 'warning' });
                } else if (args.uom.id !== productUOM.id) {
                    // Compatible but not the same UoM => Need a conversion.
                    args.inventory_quantity = (args.inventory_quantity / args.uom.factor) * productUOM.factor;
                }
            }
            line.inventory_quantity += args.inventory_quantity;
            if (line.product_id.tracking === 'serial' && (line.lot_name || line.lot_id)) {
                line.inventory_quantity = Math.max(0, Math.min(1, line.inventory_quantity));
            }
        }
    }

    async _updateLotName(line, lotName) {
        if (line.lot_name === lotName) {
            // No need to update the line's tracking number if it's already set.
            return Promise.resolve();
        }
        line.lot_name = lotName;
        // Checks if a quant exists for this line and updates the line in this case.
        const domain = [
            ['location_id', '=', line.location_id],
            ['product_id', '=', line.product_id.id],
            ['lot_id.name', '=', lotName],
            ['owner_id', '=', line.owner_id && line.owner_id.id],
            ['package_id', '=', line.package_id && line.package_id.id],
        ];
        const existingQuant = await this.orm.searchRead(
            'stock.quant',
            domain,
            ['id', 'quantity'],
            { limit: 1, load: false }
        );
        if (existingQuant.length) {
            Object.assign(line, existingQuant[0]);
            if (line.lot_id) {
                line.lot_id = await this.cache.getRecordByBarcode(lotName, 'stock.production.lot');
            }
        }
    }

    _createLinesState() {
        const lines = [];
        // Should use info in the params and not in cache instead (ids in params ?)
        Object.keys(this.cache.dbIdCache['stock.quant']).forEach((id, index) => {
            const quant = this.cache.getRecord('stock.quant', id);
            // Checks if this line is already in the quant state to get back
            // its `virtual_id` (and so, avoid to set a new `virtual_id`).
            const prevLine = this.currentState && this.currentState.lines.find(l => l.id === id);
            const previousVirtualId = prevLine && prevLine.virtual_id;
            quant.virtual_id = quant.dummy_id || previousVirtualId || this._uniqueVirtualId;
            quant.product_id = this.cache.getRecord('product.product', quant.product_id);
            quant.lot_id = quant.lot_id && this.cache.getRecord('stock.production.lot', quant.lot_id);
            quant.package_id = quant.package_id && this.cache.getRecord('stock.quant.package', quant.package_id);
            quant.owner_id = quant.owner_id && this.cache.getRecord('res.partner', quant.owner_id);
            lines.push(Object.assign({}, quant));
        });
        return lines;
    }

    _getName() {
        return _t("Inventory Adjustment");
    }

    _defaultLocationId() {
        return Object.keys(this.cache.dbIdCache['stock.location'])[0];
    }

    _defaultDestLocationId() {
        return null;
    }
}
