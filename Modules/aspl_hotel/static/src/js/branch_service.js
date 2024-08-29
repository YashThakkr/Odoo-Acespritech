/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { UPDATE_METHODS } from "@web/core/orm_service";
import { cookie } from "@web/core/browser/cookie";

const BIDS_HASH_SEPARATOR = "-";

function parseBranchIds(bidsFromHash) {
    const bids = [];
    if (typeof bidsFromHash === "string") {
        bids.push(...bidsFromHash.split(",").map(Number));
    } else if (typeof bidsFromHash === "number") {
        bids.push(bidsFromHash);
    }
    return bids;
}

function formatBranchIds(bids, separator = ",") {
    return bids.join(separator);
}

function computeAllowedBranchIds(bids) {
    const { user_branches } = session;
    if (user_branches){
        let allowedBranchIds = bids || [];
        const availableBranchesFromSession = user_branches.allowed_branches;
        const notReallyAllowedBranches = allowedBranchIds.filter(
            (id) => !(id in availableBranchesFromSession)
        );

        if (!allowedBranchIds.length || notReallyAllowedBranches.length) {
            allowedBranchIds = [user_branches.current_branch];
        }
        return allowedBranchIds;
    }
    else{
        return false
    }

}

function getBranchIdsFromBrowser(hash) {
    let bids;
    if ("bids" in hash) {
        // backward compatibility s.t. old urls (still using "," as separator) keep working
        // deprecated as of 17.0
        let separator = BIDS_HASH_SEPARATOR;
        if (typeof hash.bids === "string" && !hash.bids.includes(BIDS_HASH_SEPARATOR)) {
            separator = ",";
        }
        bids = parseBranchIds(hash.bids, separator);
    } else if (cookie.get("bids")) {
        bids = parseBranchIds(cookie.get("bids"));
    }
    return bids || [];
}

const errorHandlerRegistry = registry.category("error_handlers");
function accessErrorHandler(env, error, originalError) {
    const router = env.services.router;
    const hash = router.current.hash;
    if (!hash._branch_switching) {
        return false;
    }
    if (originalError?.exceptionName === "odoo.exceptions.AccessError") {
        const { model, id, view_type } = hash;
        if (!model || !id || view_type !== "form") {
            return false;
        }
        router.pushState({ view_type: undefined });

        browser.setTimeout(() => {
            // Force the WebClient to reload the state contained in the hash.
            env.bus.trigger("ROUTE_CHANGE");
        });
        if (error.event) {
            error.event.preventDefault();
        }
        return true;
    }
    return false;
}
export const BranchService = {
    dependencies: ["user", "router", "action"],
    start(env, { user, router, action }) {
        // Push an error handler in the registry. It needs to be before "rpcErrorHandler", which
        // has a sequence of 97. The default sequence of registry is 50.
        errorHandlerRegistry.add("accessErrorHandlerBranches", accessErrorHandler);

        const allowedBranches = session.user_branches.allowed_branches;
        const disallowedAncestorBranches = session.user_branches.disallowed_ancestor_branches;
        const allowedBranchesWithAncestors = {
            ...allowedBranches,
            ...disallowedAncestorBranches,
        };
        const activeBranchIds = computeAllowedBranchIds(
            getBranchIdsFromBrowser(router.current.hash)
        );

        // update browser data
        const bidsHash = formatBranchIds(activeBranchIds, BIDS_HASH_SEPARATOR);
        router.replaceState({ bids: bidsHash }, { lock: true });
        cookie.set("bids", formatBranchIds(activeBranchIds));
        user.updateContext({ allowed_branch_ids: activeBranchIds });

        // reload the page if changes are being done to `res.company`
        env.bus.addEventListener("RPC:RESPONSE", (ev) => {
            const { data, error } = ev.detail;
            const { model, method } = data.params;
            if (!error && model === "company.branch" && UPDATE_METHODS.includes(method)) {
                if (!browser.localStorage.getItem("running_tour")) {
                    action.doAction("reload_context");
                }
            }
        });

        return {
            allowedBranches,
            allowedBranchesWithAncestors,
            disallowedAncestorBranches,

            get activeBranchIds() {
                return allowedBranchIds.slice();
            },
            get currentBranch() {
                return availableBranches[allowedBranchIds[0]];
            },

            getBranch(branchId) {
                return allowedBranchesWithAncestors[branchId];
            },

            /**
             * @param {Array<>} companyIds - List of companies to log into
             * @param {boolean} [includeChildCompanies=true] - If true, will also
             * log into each child of each companyIds (default is true)
             */
            setCompanies(branchIds, includeChildBranches = true) {
                const newBranchIds = branchIds.length ? branchIds : [allowedBranchIds[0]];

                function addBranches(branchIds) {
                    for (const branchId of branchIds) {
                        if (!newBranchIds.includes(branchId)) {
                            newBranchIds.push(branchId);
                            addBranches(allowedBranches[branchId].child_ids);
                        }
                    }
                }

                if (includeChildBranches) {
                    addBranches(
                        branchIds.flatMap((branchId) => allowedBranches[branchId].child_ids)
                    );
                }

                const bidsHash = formatBranchIds(newBranchIds, BIDS_HASH_SEPARATOR);
                router.pushState({ bids: bidsHash }, { lock: true });
                router.pushState({ _branch_switching: true });
                cookie.set("bids", formatBranchIds(newBranchIds));
                browser.setTimeout(() => browser.location.reload()); // history.pushState is a little async
            },
        };
    },
};
//export const BranchService = {
//    dependencies: ["user", "router", "cookie"],
//    start(env, { user, router, cookie }) {
//        let bids;
//        if ("bids" in router.current.hash) {
//            bids = parseBranchIds(router.current.hash.bids);
//        } else if ("bids" in cookie.current) {
//            bids = parseBranchIds(cookie.current.bids);
//        }
//
//        let allowedBranchIds = computeAllowedBranchIds(bids);
//
//        if (allowedBranchIds){
//
//            const stringbids = allowedBranchIds.join(",");
//            router.replaceState({ bids: stringbids }, { lock: true });
//            cookie.setCookie("bids", stringbids);
//            user.updateContext({ allowed_branch_ids: allowedBranchIds });
//        }
//
//        if (session.user_branches){
//            var availableBranches = session.user_branches.allowed_branches;
//        } else{
//            var availableBranches = [];
//        }
//
//        return {
//            availableBranches,
//            get allowedBranchIds() {
//                return allowedBranchIds.slice();
//            },
//            get currentBranch() {
//                return availableBranches[allowedBranchIds[0]];
//            },
//
//            setBranches(mode, ...BranchIds) {
//                // compute next Branch ids
//                let nextBranchIds;
//                if (mode === "toggle") {
//                    nextBranchIds = symmetricalDifference(allowedBranchIds, BranchIds);
//                } else if (mode === "loginto") {
//                    const BranchId = BranchIds[0];
//                    if (allowedBranchIds.length === 1) {
//                        // 1 enabled Branch: stay in single Branch mode
//                        nextBranchIds = [BranchId];
//                    } else {
//                        // multi Branch mode
//                        nextBranchIds = [
//                            BranchId,
//                            ...allowedBranchIds.filter((id) => id !== BranchId),
//                        ];
//                    }
//                }
//                nextBranchIds = nextBranchIds.length ? nextBranchIds : [BranchIds[0]];
//                // apply them
//                    router.pushState({ bids: nextBranchIds }, { lock: true });
//                cookie.setCookie("bids", nextBranchIds);
//                browser.setTimeout(() => browser.location.reload()); // history.pushState is a little async
//            },
//        };
//    },
//};

registry.category("services").add("branch", BranchService);
