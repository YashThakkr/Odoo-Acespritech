/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class RangeField extends Component {

    get range() {
        return this.props.record.data[this.props.name] || "";
    }

}

RangeField.template = "aspl_float_slider.RangeField";

RangeField.props = {
    ...standardFieldProps,
}

export const rangeField = {
    component: RangeField,
}

registry.category("fields").add("range", rangeField);
