odoo.define('sol_ol_map_draw.solmap_common', function () {
    "use strict";
    var SolMapMixin = {
        cssLibs: [
            '/sol_ol_map_draw/static/lib/ol-6.4.3/ol.css',
            '/sol_ol_map_draw/static/lib/ol-ext/ol-ext.min.css',
        ],
        jsLibs: [
            '/sol_ol_map_draw/static/lib/ol-6.4.3/ol.js',
            '/sol_ol_map_draw/static/lib/ol-ext/ol-ext.min.js',
        ],
    };

    return {
        SolMapMixin: SolMapMixin,
    };
});