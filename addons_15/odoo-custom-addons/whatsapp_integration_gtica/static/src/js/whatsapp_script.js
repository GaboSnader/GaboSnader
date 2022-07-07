odoo.define('gtica_whatsapp_template.ScriptWhatsappOpen', function (require) {
'use strict';

var core = require('web.core');
var framework = require('web.framework');
var ActionManager = require('web.ActionManager');
var _t = core._t;

ActionManager.include({

    _executeURLAction: function (action, options) {
        var url = action.url;

        if (action.target === 'self') {
            framework.redirect(url);
            return Promise.resolve();
        } else {
            var w = '';
            if (action.name === 'whatsapp_action') {
                w = window.open(action.url , 'MyTabWhatsapp');
            }else{
                w = window.open(url, '_blank');
            }
            if (!w || w.closed || typeof w.closed === 'undefined') {
                var message = _t('A popup window has been blocked. You ' +
                             'may need to change your browser settings to allow ' +
                             'popup windows for this page.');
                this.do_warn(_t('Warning'), message, true);
            }
        }

        options.on_close();

        return Promise.resolve();
    },
});

return ActionManager;

});