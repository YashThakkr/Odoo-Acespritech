/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_service/tour_utils";
import { markup } from "@odoo/owl";


registry.category("web_tour.tours").add("loan_test_tour", {
    url: '/web?debug=1#action=aspl_employee_loan_ee.action_loan_document',
    sequence: 90,
    steps: () => [
        stepUtils.showAppsMenuItem(),
//        {
//            trigger: '.o_app[data-menu-xmlid="aspl_employee_loan_ee.action_loan_document"]',
//            content: _t(
//                "Let's try the loan app to manage the flow of creating a loan document by tour."
//            ),
//            position: "right",
//            edition: "enterprise",
//        },
        {
            trigger: ".o_list_button_add",
            extra_trigger: ".o_list_document",
            content: _t("Let's create your first loan document."),
            position: "bottom",
        },
        {
            trigger: ".o_input_name[name='name']",
//            extra_trigger: ".o_list_document",
            content: _t("Enter the name of the document."),
            position: "bottom",
            run: function (actions) {
                actions.text("Passport", this.$anchor.find("input"));
            },
        },
        {
            trigger: ".o_list_button_save",
            extra_trigger: ".o_list_view",
            content: _t("Save the document."),
            position: "bottom",
        },
        {
            trigger: ".o_list_view",
            extra_trigger: ".o_list_view",
            content: _t("The document has been saved and is listed here."),
            position: "bottom",
        },
    ],
});