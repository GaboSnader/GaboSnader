odoo.define('extras.tree_view_button', function (require){
    "use strict";       
    var core = require('web.core');
    var ListView = require('web.ListView'); 
    var ListController = require("web.ListController");

    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.modelName == 'account.move.line') {
                var your_btn = this.$buttons.find('button.o_list_button_custom_aux');
                your_btn.on('click', this.proxy('o_list_button_custom_aux'));
            }
        },
        o_list_button_custom_aux: function(){
            this.do_action({
                name: "Auxiliar Contable",
                type: 'ir.actions.act_window',
                res_model: 'wizard.accounting.assistant',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
            });
        }
    };

    ListController.include(includeDict);
});
