/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";

import { registry } from "@web/core/registry";
import { useOwnedDialogs, useBus, useService } from "@web/core/utils/hooks";
import { url } from "@web/core/utils/urls";
import { FormViewDialog } from '@web/views/view_dialogs/form_view_dialog';
import { ControlPanel } from "@web/search/control_panel/control_panel";

    export class HouseKeepingDashboard extends Component {

        setup() {
            this.actionService = useService("action");
            this.companyService = useService("company");
            this.notification = useService("notification");
            this.dialog = useService('dialog');
            this.orm = useService("orm");
            onWillStart(this.onWillStart);
        }

        async onWillStart() {
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth() + 1; //January is 0!
            var yyyy = today.getFullYear();
            today = mm + '/' + dd + '/' + yyyy;
            this.today_date = today
            var def1 = this.orm.call("work.order.detail", "search_today_work_order", [this.today_date], {

                });
            var currentUser = false
            var data = false
            await def1.then(function (resId) {
                currentUser = resId.user_name
                data = resId
            });
            this.currentUser = currentUser
            this.data = data
        }

        async work_service(e, user_id, room_id, task_name, work_order_id) {
        $(e.target).hide()
            var room_id = room_id
            var user_id = user_id
            var task_name = task_name
            var work_order_id = work_order_id;
            await this.orm.call("work.order.line", "write_work_order", [room_id, user_id, task_name, work_order_id], {}).then(function(records) {
                    if (records) {
                        $(e.target.parentElement).hide()
                        $(e.target.parentElement).parent().find('.service_order_finish').show()
                        window.location.reload(true)
                    }
                });
        }

        async openFormViewDialog(params, options = {}) {
            this.dialog.add(FormViewDialog, params, options);
        }

        async end_work_service(e, user_id, room_id, task_name, work_order_id) {
            var room_id = room_id
            var user_id = user_id
            var task_name = task_name
            var work_order_id = work_order_id;
            var context = {default_room_id: room_id,
                    default_user_id: user_id,
                    default_task_name: task_name,
                    default_work_order_id: work_order_id}
            this.openFormViewDialog({
                context,
                resModel: 'wizard.work.order',
                title: 'Work Order Remarks',
                onRecordSaved: async (record) => {
                        $(e.target.parentElement).hide()
                        $(e.target.parentElement).parent().find('.service_order_done').show()
                        window.location.reload(true)
                },
            });

        }

    }

HouseKeepingDashboard.components = {
    ControlPanel,
};

HouseKeepingDashboard.template = "aspl_hotel.HouseKeepingDashboard";

registry.category("actions").add("open_housekeeping_dashboard", HouseKeepingDashboard);