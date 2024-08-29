/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { ShippingDialogModal } from "@aspl_website_delivery_address/js/website_delivery_dialog";

    publicWidget.registry.WebsiteCartSummary = publicWidget.Widget.extend({
        selector: '.ship_address, .oe_website_sale, #shipAddress, #NewShipAddress',
        events: {
            'click .ship_add': 'open_ship_dialog',
            'click button.deliver_address': 'open_delivery_address_dialog',
        },

        init: function () {
            this._super(...arguments);
            this.rpc = this.bindService("rpc");
            this.orm = this.bindService("orm");
            this.dialog = this.bindService("dialog");
        },

        start: function () {
            return this._super.apply(this, arguments);;
        },

        open_delivery_address_dialog: function(el){
            var LineID = $(el.currentTarget).attr('data-line-id');
            this.ShippingDialogModal = new ShippingDialogModal(this.$form, {
                isWebsite: true,
                okButtonText: _t('Select'),
                cancelButtonText: _t('Cancel'),
                title: _t('Shipping Address'),
                forceDialog: this.forceDialog,
                line_id: LineID,
            }).open();

            this.ShippingDialogModal.on('confirm', null, this._onModalSubmit.bind(this, true));
            this.ShippingDialogModal.on('back', null, this._onModalSubmit.bind(this, false));

            return this.ShippingDialogModal.opened();
        },

        open_ship_dialog: function(){
            this.ShippingDialogModal = new ShippingDialogModal(this.$form, {
                isWebsite: true,
                cancelButtonText: _t('Cancel'),
                title: _t('Shipping Address'),
                forceDialog: this.forceDialog,
                line_id: false,
            }).open();

            this.ShippingDialogModal.on('back', null, this._onModalSubmit.bind(this, false));

            return this.ShippingDialogModal.opened();  
            
        },

        _onModalSubmit: function (goToPage) {
            if (goToPage) {
                window.location.pathname = "/my/home";
            } else {
                window.location.pathname = "/my/home";
            }
        },
    });

export default publicWidget.registry.WebsiteCartSummary;