/** @odoo-module **/

import dom from "@web/legacy/js/core/dom";
import publicWidget from "@web/legacy/js/public/public_widget";
import PortalSidebar from "@portal/js/portal_sidebar";

publicWidget.registry.AccountPortalSidebar = PortalSidebar.extend({
    selector: '.o_portal_invoice_sidebar',
    start: function () {
        var def = this._super.apply(this, arguments);

        var $invoiceHtml = this.$el.find('iframe#invoice_html');
        var updateIframeSize = this._updateIframeSize.bind(this, $invoiceHtml);

        $(window).on('resize', updateIframeSize);

        var iframeDoc = $invoiceHtml[0].contentDocument || $invoiceHtml[0].contentWindow.document;
        if (iframeDoc.readyState === 'complete') {
            updateIframeSize();
        } else {
            $invoiceHtml.on('load', updateIframeSize);
        }
        if ($.bbq.getState('allow_payment') === 'yes' && this.$('#o_invoice_portal_paynow').length) {
            this.$('#o_invoice_portal_paynow').trigger('click');
            $.bbq.removeState('allow_payment');
        }
        return def;
    },
});
