/** @odoo-module **/

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";

const { Component, hooks,useState } = owl;
// const { useState } = hooks;
import { session } from "@web/session";

export class SwitchBranchMenu extends Component {
    setup() {
        this.branchService = useService("branch");
        this.companyService = useService("company");
        this.actionService = useService("action");
        if(! this.branchService.currentBranch){
            this.currentBranch = this.branchService.availableBranches[0]
        }
        else{
            this.currentBranch = this.branchService.currentBranch
        }
        this.allowedBranches = this.branchService.availableBranches
        this.currentActive = this.branchService.allowedBranchIds
        this.state = useState({ branchesToToggle: [] });

    }

    toggleBranch(branchId) {
        this.state.branchesToToggle = symmetricalDifference(this.state.branchesToToggle, [
            branchId,
        ]);
        browser.clearTimeout(this.toggleTimer);
        this.toggleTimer = browser.setTimeout(() => {
            this.branchService.setBranches("toggle", ...this.state.branchesToToggle);
        }, this.constructor.toggleDelay);
    }

    logIntoBranch(branchId) {
        browser.clearTimeout(this.toggleTimer);
        if (branchId.company_id != this.companyService.currentCompany.id){
            this.actionService.doAction
            return this.actionService.doAction({
                type: 'ir.actions.client',
                tag: 'display_notification',
                params: {
                    'title': _('Warning'),
                    'message': this.companyService.currentCompany.name + _(' doesn"t have the selected branch, Please Switch the company..'),
                    'type':'warning',
                    'sticky': true,
                }
            });
        }
        this.branchService.setBranches("loginto", branchId);
    }

    get selectedBranches() {
        return symmetricalDifference(
            this.currentActive,
            this.state.branchesToToggle
        );
    }
}
SwitchBranchMenu.template = "aspl_fitness_management_ee.SwitchBranchMenu";
SwitchBranchMenu.components = { Dropdown, DropdownItem };
SwitchBranchMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: SwitchBranchMenu,
    isDisplayed(env) {
        const { availableBranches } = env.services.branch;
        if (availableBranches) {
            console.log('availableBranches-------->', Object.keys(availableBranches))
            return Object.keys(availableBranches).length > 1;
        }
        else{
            return false
        }
    },
};

registry.category("systray").add("SwitchBranchMenu", systrayItem, { sequence: 1 });


