/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Component, useState,  onMounted, onWillUnmount,} from "@odoo/owl";
//import session from 'web.session'
//import { isEventHandled, markEventHandled } from '@mail/utils/utils';
import { isEventHandled, markEventHandled } from "@web/core/utils/misc";
//import rpc from "@web/legacy/js/core/rpc";
export class HierarchyMenu extends Component {

    setup() {
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({'EmployeeData': [], 'leave_count': 0, 'isOpen': false})
        this._renderPrefix()
        onMounted(this.onMounted);
        onWillUnmount(this.onWillUnmount)
        super.setup();
        this.env.services.bus_service.addEventListener('notification', async ({ detail: notifications }) => {
            for (const { payload, type } of notifications) {
                if(type === 'update.list'){
                    await this._renderPrefix()
                }
            }
        });
    }

    onMounted() {
        document.addEventListener("click", this._onClickCaptureGlobal.bind(this), true);
    }

    onWillUnmount() {
        document.removeEventListener("click", this._onClickCaptureGlobal.bind(this), true);
    }

    async _renderPrefix() {
        const DataEmployee = await this.rpc('/get/employee/data', {});
        this.state.EmployeeData = DataEmployee
        this.state.leave_count = DataEmployee[0].length
    }

    toggleDropDown(ev) {
        ev.preventDefault();
        const targetElement = event.target;
        const documentElement = $(".o_EmployeeLeave_toggler");
        const documentIcon = $(".o_EmployeeLeave_icon");
        const documentBadge = $(".Employee_leave_badge");
        if (
            targetElement == documentElement[0] &&
            documentElement[0].contains(targetElement) ||  targetElement == documentIcon[0] &&
            documentIcon[0].contains(targetElement) ||  targetElement == documentBadge[0] &&
            documentBadge[0].contains(targetElement)
        ) {
            this.state.isOpen = !this.state.isOpen;
        }
    }

    async _on_approve(ev){
     await this.orm.call(
                    'hr.leave',
                    'action_change_status',
                    [ev]).then(function (result) {});
        window.location.reload();
        this._close_employee_leave();
    }

   async _on_reject(ev) {
        await this.orm.call(
                    'hr.leave',
                    'action_refuse_status',
                    [ev]).then(function (result) {});
        window.location.reload();
        this._close_employee_leave();
    }

    async _on_leave_days (leaveId) {
        const action = await this.orm.call('hr.leave', 'get_employee_leave_view', [false, leaveId]);
        this.actionService.doAction(action);
        this._close_employee_leave();
    }

    image(id) {
        return window.location.origin + "/web/image?model=hr.employee&field=avatar_128&id=" + id
    }

    _onClickCaptureGlobal(event) {
        const targetElement = event.target;
        const dropdownIcon = $(".o_EmployeeLeave_toggler");
        if (
            this.state.isOpen &&
            targetElement !== dropdownIcon &&
            !dropdownIcon[0].contains(targetElement)
        ) {
            this.state.isOpen = false;
        }
    }

    _close_employee_leave(){
        this.state.isOpen = false;
        $('#EmployeeLeaveToggle').hide();
        $('.o_EmployeeLeave_toggler').removeClass('bg-black-15')
    }
}

HierarchyMenu.template = "aspl_employee_leave_ee.HierarchyMenu";

HierarchyMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: HierarchyMenu,
};

registry.category("systray").add("aspl_employee_leave_ee.HierarchyMenu", systrayItem, {});
