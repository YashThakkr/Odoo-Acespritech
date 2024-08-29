/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Component, useState,  onMounted, onWillUnmount,} from "@odoo/owl";
//import rpc from "@web/legacy/js/core/rpc";

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



export class TaskMenu extends Component {

    async setup() {
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.user = useService("user");
        this.state = useState({'EmployeeData': [], 'active': false, 'isOpen': false, 'task_count': 0, 'time_limit': 0})
        this._renderPrefix()
        onMounted(this.onMounted);
        onWillUnmount(this.onWillUnmount)
        await super.setup();


        this.env.services.bus_service.addEventListener('notification', async ({ detail: notifications }) => {
            for (const { payload, type } of notifications) {
                if(type === 'update.list'){
                    await this._renderPrefix()
                    if (payload.create){
                        var url = window.location.origin + '#id=' + payload.id + '&view_type=form&model=project.task';
                        notification("success","New task assigned to you.<a href = " + url + "  style='position: relative;right: 20px;text-align: right;bottom: 19px;'>View</a> <div style='bottom: 20px; position: relative; right: 16px;'> Created by <b>" + payload.name + "</b>.</div>", payload.id)
                        setTimeout(function(){
                            $('.btn-close').click()
                        },this.state.time_limit*1000);
                    }
                }
            }
        });

    }
    onMounted() {
        window.addEventListener("click", this._onClickCaptureGlobal.bind(this), true);
    }
    onWillUnmount() {
        window.removeEventListener("click", this._onClickCaptureGlobal.bind(this), true);
    }

    async _renderPrefix() {
        const DataEmployee = await this.rpc('/get/employee/data', {});
        this.state.EmployeeData = DataEmployee
        this.state.task_count = DataEmployee.length
        if(DataEmployee[0]){
            this.state.time_limit = DataEmployee[0].time_limit}
    }
    _onClickTasks(event) {
        event.preventDefault();
        const targetElement = event.target;
        const documentElement = $(".o_EmployeeTask_toggler");
        const documentIcon = $(".o_EmployeeTask_icon");
        const documentBadge = $(".Employee_task");
        if (
          targetElement == documentElement[0] &&
          documentElement[0].contains(targetElement) ||  targetElement == documentIcon[0] &&
          documentIcon[0].contains(targetElement) ||  targetElement == documentBadge[0] &&
          documentBadge[0].contains(targetElement)
        ) {
            this.state.isOpen = !this.state.isOpen;
        }
    }
    _onClickCaptureGlobal(event) {
        const targetElement = event.target;
        const dropdownIcon = $(".o_EmployeeTask_toggler");
        if (
          this.state.isOpen &&
          targetElement !== dropdownIcon[0] &&
          !dropdownIcon[0].contains(targetElement)
        ) {
          this.state.isOpen = false;
        }
    }
    async _onClickTask(taskId) {
        const action = await this.orm.call('project.task', 'get_projectview_action', [false, taskId]);
        this.actionService.doAction(action);
        this._close_popup_task();
    }

    _close_popup_task(){
        this.state.isOpen = false;
        $('#EmployeeTaskToggle').hide();
    }
}
TaskMenu.template = "aspl_employee_task.TaskMenu";
TaskMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: TaskMenu,
};

registry.category("systray").add("aspl_employee_task.TaskMenu", systrayItem, {});

