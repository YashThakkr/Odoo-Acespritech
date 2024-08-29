/** @odoo-module */

import Dialog from '@web/legacy/js/core/dialog';
import { jsonrpc } from '@web/core/network/rpc_service';
import { _t } from "@web/core/l10n/translation";
import { ShippingDataDialogModal } from "@aspl_website_delivery_address/js/shipping_address_data";

export const ShippingDialogModal = Dialog.extend({
    events:  Object.assign({}, Dialog.prototype.events, {
        'click .new_ship_add': 'open_address_dialog',
        'click button.edit_address': '_onClickEditAddress',
        'click button.delete_address': '_onClickDeleteAddress',
        'click input.address_radio': '_onClickAddressSelect',
    }),
    
    init: function (parent, params) {
        var self = this;

        if(params.line_id){
            var options = Object.assign({
                size: 'large',
                buttons: [{
                    text: params.okButtonText,
                    click: this._onConfirmButtonClick,
                    classes: 'btn-primary o_shipping_address_dialog'
                }, {
                    text: params.cancelButtonText,
                    click: this._onCancelButtonClick
                }],
                technical: !params.isWebsite,
            }, params || {});

            this._super(parent, options);
        }
        else{
            var options = Object.assign({
                size: 'large',
                buttons: [{
                    text: params.cancelButtonText,
                    click: this._onCancelButtonClick
                }],
                technical: !params.isWebsite,
            }, params || {});

            this._super(parent, options);
        }

        this.isWebsite = params.isWebsite;
        this.forceDialog = true;

        this.dialogClass = 'oe_advanced_shipping_modal' + (params.isWebsite ? ' oe_website_sale' : '');
        this.context = params.context;
        this.container = parent;
        this.previousModalHeight = params.previousModalHeight;
        this.dialogClass = 'oe_advanced_shipping_modal';
        this.line_id = params.line_id;
        this.source = false;

        this._opened.then(function () {
            if (self.previousModalHeight) {
                self.$el.closest('.modal-content').css('min-height', self.previousModalHeight + 'px');
            }
        });

        this.orm = this.bindService("orm");
        this.rpc = this.bindService("rpc");
    },

    willStart: function () {
        var self = this;

        var getModalContent = jsonrpc("/aspl_website_delivery_address/display_shipping_address_dialog", {
            force_dialog: self.forceDialog,
            line_id: this.line_id,
        })
        .then(function (modalContent) {
            if (modalContent) {
                var $modalContent = $(modalContent);
                self.$content = $modalContent;
            } else {
                self.preventOpening = true;
            }
        });

        var parentInit = self._super.apply(self, arguments);
        return Promise.all([getModalContent, parentInit]);
    },

    open: function (options) {
        $('.tooltip').remove(); // remove open tooltip if any to prevent them staying when modal is opened

        var self = this;
        this.appendTo($('<div/>')).then(function () {
            if (!self.preventOpening) {
                self.$modal.find(".modal-body").replaceWith(self.$el);
                self.$modal.attr('open', true);
                self.$modal.appendTo(self.container);
                const modal = new Modal(self.$modal[0], {
                    focus: true,
                });
                modal.show();
                self._openedResolver();
            }
        });
        if (options && options.shouldFocusButtons) {
            self._onFocusControlButton();
        }

        return self;
    },
    
    start: function () {
        var def = this._super.apply(this, arguments);
        var self = this;

        return def;
    },

    open_address_dialog: function(){
        this.ShippingDataDialogModal = new ShippingDataDialogModal(this.$form, {
            isWebsite: true,
            okButtonText: _t('Save'),
            cancelButtonText: _t('Cancel'),
            title: _t('Add Shipping Address'),
            forceDialog: this.forceDialog,
            source: false,
        }).open();

        this.ShippingDataDialogModal.on('confirm', null, this._onModalSubmit.bind(this, true));
        this.ShippingDataDialogModal.on('back', null, this._onModalSubmit.bind(this, false));

        return this.ShippingDataDialogModal.opened();

    },

    async _onClickEditAddress(el){
        el.preventDefault();
        var EditAddID = $(el.currentTarget).val();
        var search_res = await this.orm.call("res.partner", 'search_read', [[['id', '=', EditAddID]], ['id', 'name', 'phone', 'email', 'street', 'street2', 'zip', 'city','state_id', 'country_id']]);
        var addData = search_res[0]
        this.ShippingDataDialogModal = new ShippingDataDialogModal(this.$form, {
            isWebsite: true,
            okButtonText: _t('Save'),
            cancelButtonText: _t('Cancel'),
            title: _t('Edit Shipping Address'),
            forceDialog: this.forceDialog,
            source: addData,
        }).open();

        this.ShippingDataDialogModal.on('confirm', null, this._onModalSubmit.bind(this, true));
        this.ShippingDataDialogModal.on('back', null, this._onModalSubmit.bind(this, false));

        return this.ShippingDataDialogModal.opened();
    },

    async _onClickDeleteAddress(el){
        el.preventDefault();
        var DeleteAddID = $(el.currentTarget).val();
        const check_used_address = await this.orm.call("res.partner", 'check_used_address',[false, parseInt(DeleteAddID)]);
            
        if (check_used_address == true){
            alert("you cannot delete used shipping address.")
        }
        else{
            const delete_address = await this.orm.call("res.partner", 'unlink',[parseInt(DeleteAddID)]);
            this.close();
        }
    },

    async _onClickAddressSelect(el){
        var LineID = this.line_id;
        var AddID = $(el.currentTarget).val();
        const line = this.orm.call("sale.order.line", 'add_delivery_address',[[parseInt(LineID)], AddID]);
    },

    _onModalSubmit: function (goToPage) {
        if (goToPage) {
            window.location.href = "/my/home";
        } else {
            window.location.href = "/my/home";
        }
    },

    _onConfirmButtonClick: function () {
        this.trigger('confirm');
        this.close();
    },

    _onCancelButtonClick: function () {
        this.trigger('back');
        this.close();
    },
});
