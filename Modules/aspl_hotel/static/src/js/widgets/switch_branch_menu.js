/** @odoo-module **/

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";

import { Component, useState, reactive } from "@odoo/owl";
import { session } from "@web/session";

const store = reactive({
    branchesToToggle: [],
    toggleTimer: null,
});

export class SwitchBranchItem extends Component {

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

    logIntoBranch(branchId) {
        browser.clearTimeout(this.toggleTimer);
        if (branchId.company_id != this.companyService.currentCompany.id){
            this.actionService.doAction
            return this.actionService.doAction({
                type: 'ir.actions.client',
                tag: 'display_notification',
                params: {
                    'title': ('Warning'),
                    'message': this.companyService.currentCompany.name + (' doesn"t have the selected branch, Please Switch the company..'),
                    'type':'warning',
                    'sticky': true,
                }
            });
        }
        return this.branchService.setBranches("loginto", branchId.id);
    }

    get selectedBranches() {
        return symmetricalDifference(
            this.currentActive,
            this.state.branchesToToggle
        );
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

}

SwitchBranchItem.template = 'aspl_hotel.SwitchBranchItem';
SwitchBranchItem.components = { DropdownItem, SwitchBranchItem };
SwitchBranchItem.props = {
    branch: {},
    level: {type: Number},
};
SwitchBranchItem.toggleDelay = 1000;

export class SwitchBranchMenu extends Component {
    setup() {
        this.branchService = useService("branch");
        this.store = useState(store);
        this.store.branchesToToggle = [];
    }
}

SwitchBranchMenu.template = "aspl_hotel.SwitchBranchMenu";
SwitchBranchMenu.components = { Dropdown, DropdownItem, SwitchBranchItem };
SwitchBranchMenu.props = {};

//SwitchBranchMenu.template = "aspl_hotel.SwitchBranchMenu";
//SwitchBranchMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: SwitchBranchMenu,
    isDisplayed(env) {
//        env.services.branch.currentBranch = {}
        const { availableBranches } = env.services.branch;
        if (availableBranches) {

            return Object.keys(availableBranches).length > 1;
        }
        else{
            return false
        }
    },
};

registry.category("systray").add("SwitchBranchMenu", systrayItem, { sequence: 1 });

