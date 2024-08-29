/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.GiftVoucherPage = publicWidget.Widget.extend({
    selector: ".voucher-content",

    init: function () {
        this._super.apply(this, arguments);
    },

    events: {
        "click .see-the-offer": "seeTheOffer",
    },

    seeTheOffer: function (ev) {
        ev.currentTarget.style.display = "none";
        ev.currentTarget.nextElementSibling.style.display = "";

        if ($(this.el).find(".see-the-offer-active").length) {
            $(".copy-btn").click(function () {
                var code = $(this).parent().find(".code-detail").text().trim();
                var $temp = $("<input>");
                $("body").append($temp);
                $temp.val(code).select();
                document.execCommand("copy");
                $temp.remove();
                $(this).text("COPIED");

                $(".see-the-offer-active").not($(this).parent()).each(function () {
                    $(this).hide();
                    $(this).prev().show();
                    $(this).children().eq(1).text("COPY");
                });
            });
        }
    },
});

