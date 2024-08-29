/** @odoo-module */

import Dialog from '@web/legacy/js/core/dialog';
import { jsonrpc } from '@web/core/network/rpc_service';
import { _t } from "@web/core/l10n/translation";

export const ShippingDataDialogModal = Dialog.extend({
    events: {},
    
    init: function (parent, params) {
        var self = this;

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

        this.isWebsite = params.isWebsite;
        this.forceDialog = true;

        this.dialogClass = 'oe_advanced_shipping_data_modal' + (params.isWebsite ? ' oe_website_sale' : '');
        this.context = params.context;
        this.container = parent;
        this.previousModalHeight = params.previousModalHeight;
        this.dialogClass = 'oe_advanced_shipping_data_modal';
        this.source = params.source || false;

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

        var getModalContent = jsonrpc("/aspl_website_delivery_address/shipping_address_data_dialog", {
            force_dialog: self.forceDialog,
            source: self.source,
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

    _onModalSubmit: function (goToPage) {
        if (goToPage) {
            window.location.href = "/my/home";
        } else {
            window.location.href = "/my/home";
        }
    },

    _onConfirmButtonClick: function () {
        if (!this.source){
            var name = this.$el.find('#add_name').val()
            var street = this.$el.find('#street').val()
            var street2 = this.$el.find('#street2').val()
            var zip = this.$el.find('#zip').val()
            var city = this.$el.find('#city').val()
            var state = this.$el.find('#select_state').val()
            var country = this.$el.find('#select_country').val()
            var phone = this.$el.find('#phone').val()
            var email = this.$el.find('#email').val()
            if (!name){
                alert('Please insert name.')
            }else{
                var create_add = this.orm.call("res.partner", 'create_address', [false, name, street , street2, zip, city, state, country, phone , email]);
            }
            this.trigger('confirm');
            this.close();
        }
        else{
            var partner_id = this.$el.find('#partner_id').val()
            var name = this.$el.find('#add_name').val()
            var street = this.$el.find('#street').val()
            var street2 = this.$el.find('#street2').val()
            var zip = this.$el.find('#zip').val()
            var city = this.$el.find('#city').val()
            var state = this.$el.find('#select_state').val()
            var country = this.$el.find('#select_country').val()
            var phone = this.$el.find('#phone').val()
            var email = this.$el.find('#email').val()
            if (!name){
                alert('Please insert name.')
            }else{
                var write_partner = this.orm.write("res.partner", [parseInt(partner_id)],
                    {'type': 'delivery',
                    'name': name,
                    'street': street,
                    'street2': street2,
                    'zip': zip,
                    'city': city,
                    'state_id': parseInt(state),
                    'country_id': parseInt(country),
                    'phone': phone,
                    'email': email
                });
                this.trigger('confirm');
                this.close();
            }
        }
    },

    _onCancelButtonClick: function () {
        this.trigger('back');
        this.close();
    },

 
});
