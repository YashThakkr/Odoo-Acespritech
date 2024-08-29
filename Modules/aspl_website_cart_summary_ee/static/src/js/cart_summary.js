/** @odoo-module alias=aspl_website_cart_summary_ee.cart_summary **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import wSaleUtils from "@website_sale/js/website_sale_utils";
import publicWidget from "@web/legacy/js/public/public_widget";
import { Component } from '@odoo/owl';

publicWidget.registry.WebsiteCartSummary = publicWidget.Widget.extend({
    selector: '.cart_summary',

    events: {
        'click .website_cart_summary_open': 'open_cart_summary',
        'click .custom_product_delete': 'delete_custom_product',
        'click .js_add_cart_product': 'js_add_cart_product',
        'click .js_minus_cart_product': 'js_minus_cart_product',
        'change .js_qty': 'on_change_cart_qty',
        'keypress #add_product': 'only_number_qty',
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    open_cart_summary: function (event) {
        var mySidenav = $('#mySidenav');
        var toggleIcon = $('.website_cart_summary_open i');

        mySidenav.toggle(100, function() {
            // This function runs after the animation is complete
            if (mySidenav.is(':visible')) {
                // If mySidenav is visible, change the icon to left
                toggleIcon.removeClass('fa-angle-double-left').addClass('fa-angle-double-right');
            } else {
                // If mySidenav is hidden, change the icon to right
                toggleIcon.removeClass('fa-angle-double-right').addClass('fa-angle-double-left');
            }
        });
    },

    delete_custom_product: function (event) {
        var line_id = $(event.currentTarget).next().val();
        this._updateCartSummary('/shop/cart_summary', { 'line_id': line_id });
    },

    js_add_cart_product: function (event) {
        var line_id = $(event.currentTarget).parent().prev().prev().val();
        var product_id = $(event.currentTarget).parent().prev().val();
        this._updateCartSummary('/shop/cart/update_json', {
            'line_id': parseInt(line_id),
            'product_id': parseInt(product_id),
            'add_qty': 1,
        });
    },


    js_minus_cart_product: function (event) {
        var line_id = $(event.currentTarget).parent().prev().prev().val();
        var product_id = $(event.currentTarget).parent().prev().val();
        this._updateCartSummary('/shop/cart/update_json', {
            'line_id': parseInt(line_id),
            'product_id': parseInt(product_id),
            'add_qty': -1,
        });
    },

    on_change_cart_qty: function (event) {
        var line_id = $(event.currentTarget).parent().prev().prev().val();
        var product_id = $(event.currentTarget).parent().prev().val();
        var set_qty = $(event.currentTarget).val();
        this._updateCartSummary('/shop/cart/update_json', {
            'line_id': parseInt(line_id),
            'product_id': parseInt(product_id),
            'set_qty': set_qty,
        });
    },

    only_number_qty: function (e) {
        var charCode = e.which ? e.which : e.keyCode;
        if (charCode !== 8 && charCode !== 0 && charCode !== 46 && (charCode < 48 || charCode > 57)) {
            return false;
        }
    },

    _updateCartSummary: function (url, params) {
        console.log("url", url)
        console.log("params", params)
//        this.rpc = useService("rpc");
        this.rpc(url, params).then(function (res) {
            $('.custom_uni').html(res['cart_summary']);
            window.location.reload();
        });
    },
});