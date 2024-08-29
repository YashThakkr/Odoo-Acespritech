/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.GiftVoucher = publicWidget.Widget.extend({
    selector: ".input-group, #cart_total",

    init: function () {
        this._super.apply(this, arguments);
        $("#mycar").carousel();
    },

    events: {
        "click #btn_cancel_voucher_code": "cancelVoucherCode",
        "keyup .btn-clicked": "applyVoucherOnEnter",
        "click #btn_apply_voucher_code": "applyVoucherCode",
    },

    cancelVoucherCode: function (ev) {
        var discount = $(".discount_count").text();
        jsonrpc("/discount_cancel", { discount: discount }).then(function (result) {
            if (result) {
                location.reload(true);
                $("#order_total_taxes1").hide();
            }
        });
    },

    applyVoucherCode: function (ev) {
        var code = $("#code_no").val();
        jsonrpc("/discount_cart", { code: code }).then(function (result) {
            if (result === true) {
                location.reload(true);
            } else if (result.code) {
                swal(result.code, "", "error");
            }
            $("#code_no").val("");
        });
    },

    applyVoucherOnEnter: function (ev) {
        if (ev.keyCode === 13) {
            $("#btn_apply_voucher_code").click();
        }
    },
});
