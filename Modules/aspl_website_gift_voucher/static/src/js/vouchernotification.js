/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.WebsiteCartSummary = publicWidget.Widget.extend({
    selector: "#wrapwrap, .notification",

    init: function () {
        this._super.apply(this, arguments);
        this.fetchNotification();
    },

    fetchNotification: function () {
        jsonrpc("/notification", {}).then(function (data) {
            if (data) {
                var delayTime = data.delaytime * 1000;
                if (data.detail === "pageload") {
                    this.showNotification(delayTime);
                } else if (data.detail === "intervaltime") {
                    var minute = data.minute;
                    var minuteConvert = minute * 60000;
                    setInterval(function () {
                        this.showNotification(delayTime);
                    }.bind(this), minuteConvert);
                }
            }
        }.bind(this));
    },

    showNotification: function (delayTime) {
        jsonrpc("/shownotification", {}).then(function (data) {
            if (data) {
                $.notify({
                    message: data.message,
                }, {
                    type: "pastel-info",
                    delay: delayTime,
                    template:
                        '<div data-notify="container" class="col-xs-11 col-sm-3 alert alert-{0} notification" role="alert">' +
                        '<button type="button" aria-hidden="true" class="close" data-notify="dismiss">&times;</button>' +
                        '<span data-notify="message">{2}</span>' +
                        '<button type="button" class="btn btn-primary ml-3 copy-code">COPY</button>' +
                        "</div>",
                });

                $(".copy-code").click(function () {
                    var code = $(this).closest("[data-notify='container']").find("[data-notify='message']").text().trim();
                    var $temp = $("<input>");
                    $("body").append($temp);
                    $temp.val(code).select();
                    document.execCommand("copy");
                    $temp.remove();
                    $(this).text("COPIED");
                });
            }
        });
    },
});
