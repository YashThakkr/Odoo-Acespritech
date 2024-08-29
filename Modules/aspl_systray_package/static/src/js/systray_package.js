/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Component, useState,  onMounted, onWillUnmount, onWillStart} from "@odoo/owl";
import { isEventHandled, markEventHandled } from "@web/core/utils/misc";
//import rpc from "@web/legacy/js/core/rpc";
import { session } from "@web/session";
import { useOpenChat } from "@mail/core/web/open_chat_hook";

function notification(type, message, task_id){
    var types = ['success','warning','info', 'danger'];
    if($.inArray(type.toLowerCase(),types) != -1){
    $('div.span4').remove();
    var newMessage = '';
    var url = window.location.origin + '#id=' + task_id + '&view_type=form&model=project.task';
    switch(type){
    case 'success' :
//    newMessage = message + "<a href = " + url + "  style='position: relative; left:5px;'>View</a>";
    newMessage = message;
    break;
    }
    $('body').append('<div><div class="row alert alert-warning alert-dismissible fade show" style="width: 25%; left: 35%; position:relative; padding:2px; height:40px;" role="alert">' +
                  newMessage +
                  '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="top:-8px; font-size:10px"></button>' +
                '</div></div>'
            );
        $(document).find(".alert").css('opacity',1).show();
    }
}

export class HierarchyMenu extends Component {

    async setup() {
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.user = useService("user");
        this.state = useState({'EmployeeData': [], 'active': false, 'isOpen': false, isInsideClick: false, 'time_limit': 0})
        onMounted(this.onMounted);
        onWillStart(this.onWillStart)
        onWillUnmount(this.onWillUnmount)
        this.openChat = useOpenChat('hr.employee');
        await super.setup();

        this.env.services.bus_service.addEventListener('notification', async ({ detail: notifications }) => {
            for (const { payload, type } of notifications) {
                if(type === 'update.list'){
                    await this.onWillStart();
                    if (payload.create){
                        var url = window.location.origin + '#id=' + payload.id + '&view_type=form&model=project.task';
                        notification("success", "New task assigned to you.<a href = " + url + "  style='position: relative;right: 20px;text-align: right;bottom: 19px;'>View</a> <div style='bottom: 20px; position: relative; right: 16px;'> Created by <b>" + payload.name + "</b>.</div>", payload.id);
                        const self = this;
                        setTimeout(function() {
                            $('.btn-close').click();
                        }, self.state.time_limit * 1000);
                    }
                }
            }
        });

    }

    onMounted() {
            document.addEventListener("click", this._onClickCaptureGlobal.bind(this), true);
    }

   onWillUnmount() {
        document.removeEventListener("click", this._onClickCaptureGlobal.bind(this),  true );
    }

    async onWillStart() {
        const DataEmployee = await this.rpc('/get/employee/systray', {});
        this.state.EmployeeData = DataEmployee
        if(DataEmployee[3]){
            this.state.time_limit = DataEmployee[3]
        }
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

    async _on_approve(ev){
     await this.orm.call(
                    'hr.leave',
                    'action_change_status',
                    [ev]).then(function (result) {});
        window.location.reload();
        this._close_popup_hierarchy();
    }

   async _on_reject(ev) {
        await this.orm.call(
                    'hr.leave',
                    'action_refuse_status',
                    [ev]).then(function (result) {});
        window.location.reload();
        this._close_popup_hierarchy();
    }

    async _on_leave_days (leaveID) {
        const action = await this.orm.call('hr.leave', 'get_employee_leave_view', [false, leaveID]);
        this.actionService.doAction(action);
        this._close_popup_hierarchy();
    }

    async _onClickTask(taskId) {
        const action = await this.orm.call('project.task', 'get_projecttask_action', [false, taskId]);
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

HierarchyMenu.template = "aspl_systray_package.SystrayPackage";

HierarchyMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: HierarchyMenu,
};

registry.category("systray").add("aspl_systray_package.SystrayPackage", systrayItem, {});