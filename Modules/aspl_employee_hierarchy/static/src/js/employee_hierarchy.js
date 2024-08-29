/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Component, useState,  onMounted, onWillUnmount,} from "@odoo/owl";
//import { session } from 'web.session'
import { session } from "@web/session";
//import rpc from "@web/legacy/js/core/rpc";
//import { isEventHandled, markEventHandled } from '@mail/utils/utils';
import { isEventHandled, markEventHandled } from "@web/core/utils/misc";
//import { useOpenChat } from "@mail/views/open_chat_hook";
import { useOpenChat } from "@mail/core/web/open_chat_hook";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { CheckBox } from "@web/core/checkbox/checkbox";

export class HierarchyMenu extends Component {

    setup() {
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({'EmployeeData': [], 'active': false, 'isOpen': false, isInsideClick: false,})
        this._renderPrefix()
        onMounted(this.onMounted);
        onWillUnmount(this.onWillUnmount)
        this.openChat = useOpenChat('hr.employee');
        super.setup();
    }

    onMounted() {
            document.addEventListener("click", this._onClickCaptureGlobal.bind(this), true);
    }

   onWillUnmount() {
        document.removeEventListener("click", this._onClickCaptureGlobal.bind(this),  true );
    }

//   _onCheckInOut (employeeId) {
//        this.state.active = !this.state.active;
//        this.update_attendance(employeeId);
//   }

    async _onEmployeeCount (employeeId) {
        const type = event.currentTarget.dataset.type || 'direct';
        const subordinateIds = await this.rpc('/hr/get_subordinates', {
            employee_id: employeeId,
            subordinates_type: type,
            context: session.user_context
        });
        let action = await this.orm.call('hr.employee', 'get_formview_action', [employeeId]);
        action = {...action,
            name: 'Team',
            view_mode: 'kanban,list,form',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            domain: [['id', 'in', subordinateIds]],
            res_id: false,
            context: {
                default_parent_id: employeeId,
            }
        };
        this.actionService.doAction(action);
        this._close_popup_hierarchy();
    }

    async _onChildCount (employeeId) {
        this._onEmployeeCount(employeeId);
    }

    async _renderPrefix() {
        const DataEmployee = await this.rpc('/get/employee/data', {});
        this.state.EmployeeData = DataEmployee
    }

   async _onEmployeeRedirect(employeeId) {
        const action = await this.orm.call('hr.employee', 'get_formview_action', [employeeId]);
        this.actionService.doAction(action);
         this._close_popup_hierarchy();
   }

    toggleDropDown(ev) {
        ev.preventDefault();
        const targetElement = event.target;
        const documentElement = $(".o_EmployeeHierarchy_toggler");
        const documentIcon = $(".o_EmployeeHierarchy_icon");
        if (
          targetElement == documentElement[0] &&
          documentElement[0].contains(targetElement) ||  targetElement == documentIcon[0] &&
          documentIcon[0].contains(targetElement)
        ) {
            this.state.isOpen = !this.state.isOpen;
        }
    }

//   async update_attendance(employeeId) {
//        var self = this
//        const action = await this.orm.call(
//        'hr.employee',
//        'attendance_manual',
//        [employeeId, 'hr_attendance.hr_attendance_action_my_attendances'],
//        {
//            context: session.user_context
//        }).then(function(result) {
//        });
//   }

   async _projects_employee(employeeId) {
        const action = await this.orm.call('project.task', 'get_projectview_action', [false, employeeId]);
        this.actionService.doAction(action);
        this._close_popup_hierarchy();
   }

   async _timesheet_employee(employeeId) {
        const action = await this.orm.call('account.analytic.line', 'get_timesheetview_action', [false, employeeId]);
        this.actionService.doAction(action);
        this._close_popup_hierarchy();
   }

    image(id) {
        return window.location.origin + "/web/image?model=hr.employee&field=avatar_128&id=" + id
    }

    _onClickCaptureGlobal(event) {
        const targetElement = event.target;
        const dropdownIcon = $(".o_EmployeeHierarchy_toggler");
        if (
          this.state.isOpen &&
          targetElement !== dropdownIcon[0] &&
          !dropdownIcon[0].contains(targetElement)
        ) {
          this.state.isOpen = false;
        }
    }

    _close_popup_hierarchy(){
        this.state.isOpen = false;
        $('#EmployeeHierarchyToggle').hide();
        $('.o_EmployeeHierarchy_toggler').removeClass('bg-black-15')
    }
}

HierarchyMenu.template = "aspl_employee_hierarchy.HierarchyMenu";

HierarchyMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: HierarchyMenu,
};

registry.category("systray").add("aspl_employee_hierarchy.HierarchyMenu", systrayItem, {});