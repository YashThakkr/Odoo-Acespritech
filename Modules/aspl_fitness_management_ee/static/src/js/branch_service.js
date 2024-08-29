/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { symmetricalDifference } from "@web/core/utils/arrays";
import { session } from "@web/session";

function parseBranchIds(bidsFromHash) {
    const bids = [];
    if (typeof bidsFromHash === "string") {
        bids.push(...bidsFromHash.split(",").map(Number));
    } else if (typeof bidsFromHash === "number") {
        bids.push(bidsFromHash);
    }
    return bids;
}

function computeAllowedBranchIds(bids) {
    const { user_branches } = session;
    if (user_branches){
        let allowedBranchIds = bids || [];
        const availableBranchesFromSession = user_branches.allowed_branches;
        const notReallyAllowedCompanies = allowedBranchIds.filter(
            (id) => !(id in availableBranchesFromSession)
        );

        if (!allowedBranchIds.length || notReallyAllowedCompanies.length) {
            allowedBranchIds = [user_branches.current_branch];
        }
        return allowedBranchIds;
    }
    else{
        return false
    }

}

export const BranchService = {
    dependencies: ["user", "router", "cookie"],
    start(env, { user, router, cookie }) {
        let bids;
        if ("bids" in router.current.hash) {
            bids = parseBranchIds(router.current.hash.bids);
        } else if ("bids" in cookie.current) {
            bids = parseBranchIds(cookie.current.bids);
        }

        let allowedBranchIds = computeAllowedBranchIds(bids);

        if (allowedBranchIds){

            const stringbids = allowedBranchIds.join(",");
            router.replaceState({ bids: stringbids }, { lock: true });
            cookie.setCookie("bids", stringbids);
            user.updateContext({ allowed_branch_ids: allowedBranchIds });
        }

        var availableBranches = []
        if (session.user_branches){
            var availableBranches = session.user_branches.allowed_branches;
        };

        return {
            availableBranches,
            get allowedBranchIds() {
                return allowedBranchIds.slice();
            },
            get currentBranch() {
                return availableBranches[allowedBranchIds[0]];
            },
            setBranches(mode, ...BranchIds) {
                // compute next Branch ids
                let nextBranchIds;
                if (mode === "toggle") {
                    nextBranchIds = symmetricalDifference(allowedBranchIds, BranchIds);
                } else if (mode === "loginto") {
                    const BranchId = BranchIds[0];
                    if (allowedBranchIds.length === 1) {
                        // 1 enabled Branch: stay in single Branch mode
                        nextBranchIds = [BranchId];
                    } else {
                        // multi Branch mode
                        nextBranchIds = [
                            BranchId,
                            ...allowedBranchIds.filter((id) => id !== BranchId),
                        ];
                    }
                }
                nextBranchIds = nextBranchIds.length ? nextBranchIds : [BranchIds[0]];

                // apply them
                    router.pushState({ bids: nextBranchIds }, { lock: true });
                cookie.setCookie("bids", nextBranchIds);
                browser.setTimeout(() => browser.location.reload()); // history.pushState is a little async
            },
        };
    },
};

registry.category("services").add("branch", BranchService);
