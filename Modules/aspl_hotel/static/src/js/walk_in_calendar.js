/** @odoo-module **/

import { Component, onWillStart } from "@odoo/owl";
import { busService } from "@bus/services/bus_service";
import { registry } from "@web/core/registry";
import { renderToElement } from "@web/core/utils/render";

export class ResourceView extends Component {
    setup(parent, params) {
//        title: _t('Resource View'),
//        this.action_manager = parent;
//        this.params = params;
//        this.resource_obj = false;
//        this.resourceList = [];
//        this.event_obj = [];
//        this.final_date = false,
//        this.beautician_lst = [];
//        onWillStart(this.onWillStart);
        super.setup();
    }

//     onWillStart() {
//        var self = this;
//
//    }
}


ResourceView.template = 'aspl_hotel.ResourceViewId';

//ResourceView.defaultProps = {
//    title: 'Booking details',
//};

registry.category("actions").add("tag_resource_view", ResourceView);


//odoo.define('aspl_hotel.walk_in_calendar', function (require) {
//    "use strict";
//
//    var AbstractAction = require('web.AbstractAction');
//    var Widget = require('web.Widget');
//    var rpc = require('web.rpc');
//    var core = require('web.core');
//    var QWeb = core.qweb;
//    var _t = core._t;
//    var dialogs = require('web.view_dialogs');
//    var datepicker = require('web.datepicker');
//    var Domain = require('web.Domain');
//    var Dialog = require('web.Dialog');
//    const { loadBundle } = require("@web/core/assets");
////    var ajax = require('web.ajax');
////    var session = require('web.session');
////    var field_utils = require('web.field_utils');
////    var _lt = core._lt;
////    var config = require('web.config');
////    var DropdownMenu = require('web.DropdownMenu');
//
//    var ResourceView = AbstractAction.extend( {
//            hasControlPanel: true,
//            contentTemplate: 'ResourceViewId',
//
//        events: {
//            'change .o_searchview_extended_prop_field': 'changed',
//            'change .o_searchview_extended_prop_op': 'operator_changed',
//            'click .o_searchview_extended_delete_prop': function (e) {
//                e.stopPropagation();
//                this.trigger_up('hotel_remove_proposition');
//            },
//            'keyup .o_searchview_extended_prop_value': function (ev) {
//                if (ev.which === $.ui.keyCode.ENTER) {
//                    var abc = this.trigger_up('hotel_confirm_proposition');
//                }
//            },
//            'click .o_apply_hotel_filter': '_onHotelApplyClick',
//            'click .o_add_custom_filter': 'add_custom_filter',
//            'click .autocomplete_li': 'autocomplete_click',
//            'click .o_hotel_facet_remove': 'remove_hotel_filter',
//            'click .ibox-tools': 'removeEvent',
//        },
//
//        custom_events: _.extend({}, AbstractAction.prototype.custom_events, {
//            hotel_remove_proposition: '_onHotelRemoveProposition',
//            hotel_confirm_proposition: '_onHotelConfirmProposition',
//            hotel_new_filters: '_onHotelNewFilters',
//        }),
//
//        init: function (parent, action,context) {
//            this._super.apply(this, arguments);
//            var self = this;
//            this.action_manager = parent;
//            self.get_title = false;
//            self.resource_obj = false;
//            self.event_obj = false;
//            self.first_start = false;
//            self.first_end = false;
//            self.second_start = false;
//            self.second_end = false;
//            self.final_date = false,
//            self.cust_list = [];
//            self.color_dict = false;
//            self.calendar_cust_search_string = '';
//            self.highlight_dates = [];
//            this.filtersMapping = [];
//            self.beautician_lst = [];
//            self.event_date_list = []
//            this.items = [];
//            this.hotel_domain = [];
//            var fields = {
//                name: {
//                    change_default: false,
//                    company_dependent: false,
//                    depends: [],
//                    manual: false,
//                    readonly: false,
//                    required: true,
//                    display_name: 'F',
//                    searchable: true,
//                    sortable: true,
//                    store: true,
//                    string: "Name",
//                    translate: false,
//                    trim: true,
//                    type: "char",
//                },
//                room_id: {
//                    change_default: false,
//                    display_name: 'A',
//                    company_dependent: false,
//                    context: {},
//                    depends: [],
//                    domain: [],
//                    manual: false,
//                    readonly: false,
//                    relation: "hotel.room",
//                    required: true,
//                    searchable: true,
//                    sortable: true,
//                    store: true,
//                    string: "Room",
//                    type: "many2one",
//                },
//                room_type_id:{
//                    change_default: false,
//                    company_dependent: false,
//                    display_name: 'B',
//                    context: {},
//                    depends: [],
//                    domain: [],
//                    manual: false,
//                    readonly: false,
//                    relation: "hotel.room.type",
//                    required: true,
//                    searchable: true,
//                    sortable: true,
//                    store: true,
//                    string: "Room Type",
//                    type: "many2one",
//                },
//                state: {
//                    change_default: false,
//                    company_dependent: false,
//                    depends: [],
//                    display_name: 'C',
//                    manual: false,
//                    readonly: false,
//                    required: false,
//                    searchable: true,
//                    selection: [["walk_in", "Walk In"], ["reserve", "Reserve"], ["check_in", "Check In"], ["check_out", "Check Out"]],
//                    sortable: true,
//                    store: true,
//                    string: "Status",
//                    type: "selection",
//                },
//                status:{
//                    change_default: false,
//                    company_dependent: false,
//                    depends: [],
//                    manual: false,
//                    display_name: 'D',
//                    readonly: false,
//                    required: false,
//                    searchable: true,
//                    selection: [["available", "Available"], ["booked", "Booked"], ["occupied", "Occupied"]],
//                    length: 3,
//                    sortable: true,
//                    store: true,
//                    string: "Room Status",
//                    type: "selection",
//                },
//            }
//        this.propositions = [];
//        this.fields = _(fields).chain()
//            .map(function (val, key) { return _.extend({}, val, {'name': key}); })
//            .filter(function (field) { return !field.deprecated && field.searchable; })
//            .sortBy(function (field) {return field.string;})
//            .value();
//        this.attrs = {_: _, fields: this.fields, selected: null};
//        this.value = null;
//        this.items = []
//        },
//
//        willStart: function() {
//            var self = this;
//            return Promise.all([loadBundle(this), this._super()]).then(function() {
//                return self.fetch_data();
//            }).then(function(){
//                var website = _.findWhere(self.websites, {selected: true});
//                self.website_id = website ? website.id : false;
//                });
//        },
//
//        fetch_data: function() {
//            var self = this;
//        },
//
//        start: function () {
//            return this._super().then(function() {
//            });
//        },
//
//        on_attach_callback: function () {
//            this._isInDom = true;
//            this._super.apply(this, arguments);
//        },
//        on_detach_callback: function () {
//            this._isInDom = false;
//            this._super.apply(this, arguments);
//        },
//
//        render_dashboards: function() {
//            var self = this;
//            _.each(this.dashboards_templates, function(template) {
//                self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self}));
//            });
//        },
//
//        on_reverse_breadcrumb: function() {
//            var self = this;
//            web_client.do_push_state({});
//            this.fetch_data().then(function() {
//                self.$('.o_website_dashboard').empty();
//                self.render_dashboards();
//            });
//        },
//
//        autocomplete_click: function(e){
//            var self = this;
//            var domain = []
//            var domain_string = false
//            if ($(e.currentTarget).attr('data-name') == 'name'){
////                $(e.currentTarget).context.children[1].innerHTM
//                domain.push('name', 'ilike', e.currentTarget.children[1].innerHTML)
//                domain_string = 'Name contains "' + e.currentTarget.children[1].innerHTML + '"'
//            }
//            if ($(e.currentTarget).attr('data-name') == 'number'){
//                domain.push('number', 'ilike', e.currentTarget.children[1].innerHTML)
//                domain_string = 'Number contains "' + e.currentTarget.children[1].innerHTML + '"'
//            }
//            if ($(e.currentTarget).attr('data-name') == 'contact'){
//                domain.push('mobile_no', 'ilike', e.currentTarget.children[1].innerHTML)
//                domain_string = 'Contact Number contains "' + e.currentTarget.children[1].innerHTML + '"'
//            }
//            $('.o_hotel_searchview_autocomplete').hide()
//            var html = '<div aria-label="search" class="o_searchview_facet" role="img" tabindex="0">'
//            html += '<span class="fa fa-filter o_searchview_facet_label"></span>'
//            html += '<div class="o_facet_values">'
//            html += '<span>' + domain_string + '</span>'
//            html += '</div>'
//            html += '<div aria-label="Remove" class="fa fa-sm fa-remove o_hotel_facet_remove" role="img" title="Remove"></div>'
//            html += '</div>'
//
//            $('.o_hotel_searchview_input_container .o_hotel_searchview_autocomplete').after(html)
////            $('#backend_resource_view').fullCalendar('destroy');
//            $('#backend_resource_view').fullCalendar('removeEvents')
//            self.prepareResourceView(domain)
//            $('.o_hotel_searchview_input').val('')
//            setTimeout(function(){
//            $('#backend_resource_view').fullCalendar('removeEvents');
//            $('#backend_resource_view').fullCalendar('renderEvent', self.eventList)
//            $('#backend_resource_view').fullCalendar('addEventSource', self.eventList);
//            $('#backend_resource_view').fullCalendar('refetchEvents');
//            },1000)
//        },
//
//        remove_hotel_filter: function(e){
//            $(e.currentTarget).parent().remove()
//            window.location.reload();
//        },
//
//        removeEvent : function(e){
//            var self = this;
//            console.log(">>>>>>>>>>>>>>>>>>>>>>>.thhhis", this, $(e.currentTarget).attr('walk_in_id'))
//            if (confirm("Are you sure you want to delete ?")) {
//                rpc.query({
//                    model: 'walk.in.detail',
//                    method: 'remove_booking',
//                    args : [[$(e.currentTarget).attr('walk_in_id'), $(e.currentTarget).attr('data-id')]]
//                }, {async: false}).then(function (res) {
//                    if(res){
//                        var new_event_object = _.reject(self.event_obj, {'id': parseInt($(e.currentTarget).attr('data-id'))});
//                        self.event_obj = new_event_object;
//                    }
//                });
//            }
//        },
//
//        date_display_or_select: function(){
//            $("#select_date").datepicker({
//                showOn: "button",
//                buttonText: "<i class='fa fa-calendar'></i>",
//                onSelect: function(dateText) {
//                    $('#backend_resource_view').fullCalendar('gotoDate', moment(dateText).format('YYYY-MM-DD'));
//                    $('.title-display').html(self.get_title)
//                }
//            });
//		},
//
//        renderElement: function() {
//            var self = this;
//            this._super.apply(this, arguments);
//            var user_ids = [];
//            setTimeout(function () {
////                rpc.query({
////                    model: 'company.branch',
////                    method: 'search_read',
////                    fields: ['id', 'name'],
////                }, {
////                    async: false
////                }).then(function (branch_ids) {
////                    var room_type_html = QWeb.render('branch_template', {
////                        branch_ids: branch_ids,
////                        widget: self,
////                    });
////                    self.$el.find('#branch_selection').empty();
////                    self.$el.find('#branch_selection').append(room_type_html);
////                });
//                rpc.query({
//                    model: 'hotel.room.type',
//                    method: 'search_read',
//                    fields: ['id', 'name'],
//                }, {
//                    async: false
//                }).then(function (room_type) {
//                    var room_type_html = QWeb.render('floor_template', {
//                        room_type: room_type,
//                        widget: self,
//                    });
//                    self.$el.find('#floor_selection').empty();
//                    self.$el.find('#floor_selection').append(room_type_html);
//                });
//                var filter_template_html = QWeb.render('filter_template', {
//                    widget: self
//                });
//                self.$el.find('#advance_search').empty();
//                self.$el.find('#advance_search').append(filter_template_html);
//                this.$('#cal_cust_search').autocomplete({
//                    source: function (request, response) {
//                        var query = request.term;
//                        var search_timeout = null;
//                        self.loaded_partners = [];
//                        if (query) {
//                            search_timeout = setTimeout(function () {
//                                var partners_list = [];
//                                self.loaded_partners = self.load_partners(query);
//                                _.each(self.loaded_partners, function (partner) {
//                                    partners_list.push({
//                                        'id': partner.id,
//                                        'value': partner.name,
//                                        'label': partner.name
//                                    });
//                                });
//                                response(partners_list);
//                            }, 70);
//                        }
//                    },
//
//                    select: function (event, partner) {
//                        event.stopImmediatePropagation();
//                        if (partner.item && partner.item.id) {
//                            var selected_partner = _.find(self.loaded_partners, function (customer) {
//                                return customer.id == partner.item.id;
//                            });
//
//                            var highlight_dates = [];
//                            _.find(self.event_obj, function (customer) {
//                                if (customer.partner_id === selected_partner.id) {
//                                    highlight_dates.push(moment(customer.start, 'YYYY-MM_DD').format('D-M-YYYY'));
//                                }
//                            });
//                            self.highlight_dates = highlight_dates;
//                            if (highlight_dates && highlight_dates.length > 0) {
//                                $(".ui-datepicker-trigger").trigger("click");
//                                                                $('#ui-datepicker-div').show();
//                            } else {
//                                self.highlight_dates = [];
//                            }
//                        }
//                    },
//                    focus: function (event, ui) {
//                        event.preventDefault(); // Prevent the default focus behavior.
//                    },
//                    close: function (event) {
//                        // it is necessary to prevent ESC key from propagating to field
//                        // root, to prevent unwanted discard operations.
//                        if (event.which === $.ui.keyCode.ESCAPE) {
//                            event.stopPropagation();
//                        }
//                    },
//                    autoFocus: true,
//                    html: true,
//                    minLength: 1,
//                    delay: 200
//                });
//                self.prepareResourceView();
//                $('button.o_dropdown_toggler_btn').on('click', function(e){
//                    e.preventDefault()
//                    e.stopPropagation();
//                    this.generatorMenuIsOpen = !this.generatorMenuIsOpen;
//                    var def;
//                    if (!this.generatorMenuIsOpen) {
//                        _.invoke(this.propositions, 'destroy');
//                        this.propositions = [];
//                    }
//                    $('.o_filters_menu').toggle()
//                    self.changed()
//                });
//
//                $("#room_type_ids").select2({
//                    placeholder: "Room Type",
//                    allowClear: true,
//                });
//
//                $("#select_filter").select2({
//                    placeholder: "Filter",
//                    allowClear: true,
//                });
//
//                $('#branch_selection').change(function (e) {
//                    var branch_id = $('#branch_id_select').val()
//                    $('#backend_resource_view').fullCalendar('destroy');
//                    self.prepareResourceView()
//                    self.date_display_or_select()
//                });
//
//                $('#select_filter').change(function (e) {
//                });
//
//                $('.o_hotel_searchview_input').keyup(function(event){
//                    var keycode = (event.keyCode ? event.keyCode : event.which);
//                    var li = $('.o_hotel_searchview_autocomplete li');
//                    var liSelected;
//                    if(keycode == 40){
//                        if(! liSelected){
//                            liSelected = $('.o_hotel_searchview_autocomplete li.o-selection-focus')
//                            liSelected.removeClass('o-selection-focus');
//                            var next = liSelected.next();
//                            if(next.length > 0){
//                                liSelected = next.addClass('o-selection-focus');
//                            }else{
//                                liSelected = li.eq(0).addClass('o-selection-focus');
//                            }
//                        }else{
//                            liSelected = li.eq(0).addClass('o-selection-focus');
//                        }
//                    }
//                    else if(keycode == 38){
//                        if(! liSelected){
//                            liSelected = $('.o_hotel_searchview_autocomplete li.o-selection-focus')
//                            liSelected.removeClass('o-selection-focus');
//                            var next = liSelected.prev();
//                             if(next.length > 0){
//                                liSelected = next.addClass('o-selection-focus');
//                            }else{
//                                liSelected = li.last().addClass('o-selection-focus');
//                            }
//                        }else{
//                            liSelected = li.last().addClass('o-selection-focus');
//                        }
//                    }
//                    if(keycode == '13'){
//                        $(this).parents('.o_hotel_searchview_input_container').find('.o_hotel_searchview_autocomplete li.o-selection-focus').trigger('click')
////                        self.autocomplete_click($(this).parents('.o_hotel_searchview_input_container').find('.o_hotel_searchview_autocomplete li.o-selection-focus'))
//                    }
//                    if(keycode == 8){
//                    	$('.o_hotel_facet_remove').trigger('click');
//                    }
//                    if($('.o_hotel_searchview_input').val()){
//                        $('.o_hotel_searchview_autocomplete').show()
//                        $('.o_hotel_searchview_autocomplete li strong').html($('.o_hotel_searchview_input').val())
//                    }
//                    else{
//                        $('.o_hotel_searchview_autocomplete li strong').html($('.o_hotel_searchview_input').val())
//                    }
//                });
//
//                $('.autocomplete_li').mouseover(function (e){
//                    $(e.currentTarget).addClass('o-selection-focus');
//                });
//                $('.autocomplete_li').mouseout(function (e){
//                    $(e.currentTarget).removeClass('o-selection-focus');
//                });
//
//                $('#room_type_ids').change(function (e) {
//                    var select_val = $(e.currentTarget).val();
//                    var data = $('#room_floor').select2('data');
//                    var res_id = []
//                    var filter_id_list = [];
//                    _.each(data, function (each) {
//                        filter_id_list.push(parseInt(each.id))
//                    });
//
//                    if (data && data.length > 0) {
//                        _.each(self.beautician_expert_in, function (each) {
//                            var chack = each.expert_in.some(v => filter_id_list.includes(v))
//                            if (chack) {
//                                var user_id = _.contains(res_id, each.id);
//                                if (!user_id) {
//                                    res_id.push(each.id);
//                                }
//                            }
//                        });
//                    }
//
//                    if (res_id) {
//                        self.beautician_lst = _.union(self.beautician_lst, res_id)
//                        var new_resource_id_list = []
//                        _.each(self.beautician_lst, function (each) {
//                            if (_.contains(res_id, each)) {
//                                new_resource_id_list.push(each);
//                            }
//                        });
//                        self.beautician_lst = new_resource_id_list;
//                    }
//                    if (data.length === 0) {
//                        self.beautician_lst = _.union(self.beautician_lst, user_ids)
//                    }
//                    $('#backend_resource_view').fullCalendar('refetchResources');
//                    $('.fc-divider').find('.fc-cell-content').addClass('fc-expander');
//                });
//                $('#branch_selection').change(function (e) {
//                    var select_val = $(e.currentTarget).val();
//                    var data = $('#room_floor').select2('data');
//                    var res_id = []
//                    var filter_id_list = [];
//                    _.each(data, function (each) {
//                        filter_id_list.push(parseInt(each.id))
//                    });
//
//                    if (data && data.length > 0) {
//                        _.each(self.beautician_expert_in, function (each) {
//                            var chack = each.expert_in.some(v => filter_id_list.includes(v))
//                            if (chack) {
//                                var user_id = _.contains(res_id, each.id);
//                                if (!user_id) {
//                                    res_id.push(each.id);
//                                }
//                            }
//                        });
//                    }
//
//                    if (res_id) {
//                        self.beautician_lst = _.union(self.beautician_lst, res_id)
//                        var new_resource_id_list = []
//                        _.each(self.beautician_lst, function (each) {
//                            if (_.contains(res_id, each)) {
//                                new_resource_id_list.push(each);
//                            }
//                        });
//                        self.beautician_lst = new_resource_id_list;
//                    }
//                    if (data.length === 0) {
//                        self.beautician_lst = _.union(self.beautician_lst, user_ids)
//                    }
//                    $('#backend_resource_view').fullCalendar('refetchResources');
//                    $('.fc-divider').find('.fc-cell-content').addClass('fc-expander');
//                });
//            }, 1000);
//        },
//
//        _onHotelNewFilters: function (event) {
//            var self= this;
//            var filter;
//            var filters = [];
//            var groupId;
//            _.each(event.data, function (filterDescription) {
//                if(filterDescription.filter.attrs.domain){
//                    self.hotel_domain.push(filterDescription.filter.attrs.domain)
//                    filter = new search_inputs.Filter(filterDescription.filter, self);
//                    filters.push(filter);
//                    self.filtersMapping.push({
//                        filterId: filterDescription.itemId,
//                        filter: filter,
//                        groupId: filterDescription.groupId,
//                    });
//                    // filters belong to the same group
//                    if (!groupId) {
//                        groupId = filterDescription.groupId;
//                    }
//                }
//            });
//            var group = new search_inputs.FilterGroup(filters, this, [], []);
//            filters.forEach(function (filter) {
//                group.toggle(filter, {silent: true});
//            });
//        },
//
//        /**
//         * Confirm a filter selection, creates it and add it to the menu
//         *
//         * @private
//         */
//
//        /**
//         * override
//         *
//         * @private
//         * @param {Object} item
//         */
//         _hotelprepareItem: function (item) {
//            if (item.isPeriod) {
//                item.options = this.periodOptions;
//            }
//
//        },
//        /**
//         * override
//         *
//         * @private
//         */
//
//        /**
//         * Hide and display the sub menu which allows adding custom filters
//         *
//         * @private
//         */
//
//
//        //--------------------------------------------------------------------------
//        // Handlers
//        //--------------------------------------------------------------------------
//
//        /**
//         * @private
//         * @param {MouseEvent} event
//         */
//
//
//        /**
//         * @private
//         * @param {MouseEvent} event
//         */
//        _onHotelApplyClick: function (event) {
//            var args = false;
////            args =  filterMenu.prototype._onApplyClick(event,this)
//            this._hotelcommitSearch();
//        },
//
//        _hotelcommitSearch: function () {
//            var self = this;
////            var filters = _.invoke(this.propositions, 'get_filter');
//            var filters = self.hotel_get_filter()
//            _.each(filters, function (filter) {
//                if(filter.domain){
//                    filter.domain = Domain.prototype.arrayToString(filter.domain);
//                    filter.modifiers = {}
//                }
//            });
//
//            var groupId = _.uniqueId('__group__');
//            var data = [];
//
//            _.each(filters, function (filter) {
//                var filterName = _.uniqueId('__filter__');
//                var filterItem = {
//                    itemId: filterName,
//                    description: filter.string,
//                    groupId: groupId,
//                    isActive: true,
//                };
//                self._hotelprepareItem(filterItem);
//                data.push({
//                    itemId: filterName,
//                    groupId: groupId,
//                    filter: {'attrs':filter},
//                });
//                self.items.push(filterItem);
//            });
//            this.trigger_up('hotel_new_filters', data);
////            _.invoke(this.propositions, 'destroy');
//            this.propositions = [];
//        },
//
//        /**
//         * @private
//         * @param {OdooEvent} event
//         */
//        _onHotelConfirmProposition: function (event) {
//            event.stopPropagation();
//            this._hotelcommitSearch();
//        },
//        /**
//         * @private
//         * @param {OdooEvent} event
//         */
//
//        hotel_get_filter: function () {
//            if (this.attrs.selected === null || this.attrs.selected === undefined)
//                return null;
//            var field = this.attrs.selected,
//                op_select = this.$('.o_searchview_extended_prop_op')[0],
//                operator = op_select.options[op_select.selectedIndex];
//            return {
//                attrs: {
//                    domain: this.value.get_domain(field, operator),
//                    string: this.value.get_label(field, operator),
//                },
//                children: [],
//                tag: 'filter',
//            };
//        },
//
//        prepareResourceView: function (moment_date) {
//            var self = this;
//            var resourceList = false;
//            var eventList = false;
//            var color_dict = false;
//            var buttonchecklist = false;
//            setTimeout(function(){
//                $(document).ready(function(){
//                var counter = -1;
//                rpc.query({
//                    model: 'walk.in.detail',
//                    method: 'get_resource_view_data',
//                    args: [moment_date ? parseInt(moment(moment_date).weekday()) : parseInt(moment().weekday()), moment_date]
//                }, {
//                    async: false
//                }).then(function (res) {
//                    resourceList = res[0];
//                    if (res[1].length){
//                        self.eventList = res[1];
//                    }
//                    else{
//                        self.eventList = false;
//                    }
//                    color_dict = res[2];
//                    self.event_obj = eventList;
//                    self.event_date_list = eventList;
//                    self.buttonchecklist = self.eventList
//                });
//                setTimeout(function(){
//                    self.$el.find('#backend_resource_view').fullCalendar({
//                    defaultView: 'week',
//                    defaultDate: moment_date ? moment(moment_date).format('YYYY-MM-DD') : moment(),
//                    aspectRatio: 1.5,
//                    editable: true,
//                    displayEventEnd: true,
//                    allDaySlot: false,
//                    eventOverlap: false,
//                    selectable: true,
//                    height: 550,
//                    resourceAreaWidth: "17%",
//                    slotDuration: '00:00',
//                    eventLimit: true, // allow "more" link when too many eventsfullcalendar
//                    customButtons: {
//                        myCustomNextButton: {
//                            text: 'Next',
//                            click: function() {
//                                if (self.buttonchecklist.length){
//                                    counter = counter + 1;
//                                    if(counter >= self.buttonchecklist.length){
//                                        counter = self.buttonchecklist.length
//                                        $('.fc-myCustomNextButton-button').css("pointer-events", 'none');
//                                        $('.fc-myCustomNextButton-button').attr("disabled", true);
//                                    }
//                                    else{
//                                        self.$el.find('#backend_resource_view').fullCalendar('gotoDate', moment(self.buttonchecklist[counter].start));
//                                        $('.fc-myCustomPrevButton-button').css("pointer-events", '');
//                                        $('.fc-myCustomPrevButton-button').attr("disabled", false);
//                                    }
//                                }
//                            }
//                        },
//                        myCustomPrevButton: {
//                            text: 'Prev',
//                            click: function() {
//                                if(self.buttonchecklist.length){
//                                    if (counter == 0){
//                                        counter = 0
//                                        $('#backend_resource_view').fullCalendar('gotoDate', moment(self.buttonchecklist[counter].start));
//                                    }
//                                    else{
//                                        counter = counter - 1;
//                                    }
//                                    if(counter <= 0){
//                                        counter = 0;
//                                        $('#backend_resource_view').fullCalendar('gotoDate', moment(self.buttonchecklist[counter].start));
//                                        $('.fc-myCustomPrevButton-button').css("pointer-events", 'none');
//                                        $('.fc-myCustomPrevButton-button').attr("disabled", true);
//                                    }
//                                    else{
//                                        $('#backend_resource_view').fullCalendar('gotoDate', moment(self.buttonchecklist[counter].start));
//                                        $('.fc-myCustomNextButton-button').css("pointer-events", '');
//                                        $('.fc-myCustomNextButton-button').attr("disabled", false);
//                                    }
//                                }
//                            }
//                        }
//                    },
//                    header: {
//                        left: 'prev, today, next',
//                        center: 'title',
//                        right: 'myCustomPrevButton, myCustomNextButton, month,week',
//                    },
//                    buttonText: {
//                        month: 'Month',
//                        today: 'Today',
//                    },
//                    views: {
//                        week: {
//                            type: 'timeline',
//                            duration: {
//                                weeks: 1
//                            },
//                            slotDuration: {
//                                days: 1
//                            },
//                            buttonText: 'Week',
//                            columnHeaderFormat: 'ddd M/D'
//                        },
//                        month: {
//                            editable: false,
//                            selectable: false,
//                        }
//                    },
//                    resourceColumns: [{
//                        labelText: 'Rooms',
//                        field: 'title'
//                    }],
//                    resourceGroupField: 'building',
//                    resources: resourceList,
//
//                    eventDrop: function (event) {
//                        if (event.status == 'check_out'){
//                            return false;
//                        }else{
//
//                        var transferReasonDialog=new Dialog(this, {
//                            title: "Room Transfer Reason",
//                            size: 'medium',
//                            dialogClass: 'room_transfer_reason',
//                            $content:$('<div><input type="text" name="close_reason" class="room_transfer_reason" placeholder="Reason..."/></div>'),
//                            buttons: [{
//                                text: 'Transfer',
//                                classes: 'btn-primary',
//                                close: true,
//                                click: function (e) {
//                                    var reason = this.$el.find('.room_transfer_reason').val()
//                                    rpc.query({
//                                            model: 'walk.in.detail',
//                                            method: 'update_resource_view_event_drop',
//                                            args: [event.walk_in_id,
//                                                parseInt(event.room_no),
//                                                parseInt(event.resourceId),
//                                                moment(event.start).format('YYYY-MM-DD HH:mm:ss'),
//                                                moment(event.end).format('YYYY-MM-DD HH:mm:ss'),
//                                                moment(event.start).format('YYYY-MM-DD'),
//                                                moment(event.end).format('YYYY-MM-DD'),
//                                                reason,
//                                            ]
//                                            }, {
//                                                async: false
//                                            });
//                                    $('#backend_resource_view').fullCalendar('destroy');
//                                    self.prepareResourceView()
//                                },
//                                },
//                                {
//                                    text: _t("Cancel"),
//                                    close: true,
//                                    click: function (e) {
//                                        $('#backend_resource_view').fullCalendar('destroy');
//                                        self.prepareResourceView()
//                                    },
//                                }],
//                        }).open();
//                            }
//                    },
//
////                    eventAllow: function(dropInfo, draggedEvent) {
////                        if (draggedEvent.status == 'check_out'){
////                            return false;
////                        }
////                    },
//
//                    /*EVENT RESIZE*/
//                    eventResize: function (event) {
//                        var params = {
//                            model: 'walk.in.detail',
//                            method: 'update_resource_view_event_resize',
//                            args: [parseInt(event.id),
//                                moment(event.start).format("YYYY-MM-DD HH:mm:ss"),
//                                moment(event.end).format("YYYY-MM-DD HH:mm:ss"),
//                            ],
//                        }
//                        rpc.query(params, {
//                                async: false
//                            })
//                            .then(function (res) {
//
//                            });
//                    },
//                    eventClick: function (event, element) {
//                        var self = this;
//                    },
//
//                    events: self.eventList,
//
//                    _onNotification: function(notifications){
//                        var self = this;
//                         for (var notif of notifications) {
//                            if(notif[1] && notif[1].event){
//                                if(self.event_id && self.event_id == notif[1].event.id){
//                                }else{
//                                    self.renderEvent(notif[1].event);
//                                    self.event_id = notif[1]['event']['id'];
//                                    self.event_obj.push(notif[1].event);
//                                }
//                            }else if(notif[1].remove_event){
//                                self.event_obj = _.filter(self.event_obj, function(item) {
//                                     return item.id !== Number(notif[1].remove_event)
//                                });
//                                $('#backend_resource_view').fullCalendar('removeEvents', notif[1].remove_event);
//                            }else if(notif[1].drag_drop_event){
//                                var update_event = false;
//                                _.map(self.event_obj, function(obj){
//                                    if(obj.id === Number(notif[1].drag_drop_event.id)) {
//                                        update_event = obj
//                                    }
//                                })
//                                self.event_obj = _.filter(self.event_obj, function(item) {
//                                     return item.id !== Number(notif[1].drag_drop_event.id)
//                                });
//
//                                update_event['start'] = notif[1].drag_drop_event.start;
//                                update_event['end'] = notif[1].drag_drop_event.end;
//                                update_event['resourceId'] = notif[1].drag_drop_event.assigned_to;
//                                self.event_obj.push(update_event);
//
//                                $("#backend_resource_view").fullCalendar('removeEvents', notif[1].drag_drop_event.id);
//                                self.renderEvent(update_event);
//                            }else if(notif[1].eventResize){
//                                _.map(self.event_obj, function(obj){
//                                    if(obj.id == notif[1].eventResize.id) {
//                                        obj.start = notif[1].eventResize.start;
//                                        obj.end = notif[1].eventResize.end;
//                                    }
//                                })
//                                $("#backend_resource_view").fullCalendar('removeEvents', );
//                                self.renderEvent(self.event_obj);
//                            }else if(notif[1].eventLeave){
//                                self.event_obj.push(notif[1].eventLeave);
//                                self.renderEvent(notif[1].eventLeave);
//                            }
//                        }
//                    },
//
//                    eventRender: function (events, element) {
//                        console.log("\n\n\n events , element", events, element)
////                        element.popover({
////                            title: events.number,
////                            animation:true,
////                            delay: 200,
////                            content: '<b>Customer : </b> '+ events.customer +"<br/><b>Room No : </b> "+ events.room_no,
////                            trigger: 'hover',
////                            html: true
////                        });
////                        $(element).css({
////                            "font-weight": "bold",
////                            'font-size': '12px'
////                        });
//                        if (events['rendering'] === 'background') {
//                        } else {
//                            var id = events.id;
//                            console.log("event_renderer..........", events)
//                            element.prepend("<div data-id=" + id + " walk_in_id=" + events.walk_in_id + " class='ibox-tools' style='cursor:pointer;float:right;position:relative;height:20px;width: auto;z-index: 1000;'><a style='position:relative;background-color: transparent; margin-right: 12px;height: auto;' class='testing pull-left'><i class='fa fa-times remove_booking' data-id=" + id + " style='position:absolute;color: white;margin-top: 3px;'></i></a></div>");
//                        }
////                        element.find(".remove_booking").click(function (e) {
////                            console.log("\n\n\n confirm",confirm)
////                            if (confirm('Are you sure you want to delete ?')) {
////                                console.log("\n\n\n events.id",events._id)
////                                $('#backend_resource_view').fullCalendar('removeEvents', events._id);
////                                rpc.query({
////                                    model: 'walk.in.detail',
////                                    method: 'remove_booking',
////                                    args: [$(e.currentTarget).attr('data-id')]
////                                }, {
////                                    async: false
////                                }).then(function (res) {
////                                    console.log("\n\n\n res", res)
////                                    if(res == false){
////                                        alert('You can not delete record!!!!!')
////                                    }
////                                    else{
////                                        $('#backend_resource_view').fullCalendar('removeEvents', events._id);
////                                        return true;
////                                    }
////                                });
////                            } else {}
////                        });
//                    },
//
//                    eventAfterAllRender: function () {
//                        self.isSwipeEnabled = true;
//                    },
//
//
//                    resourceRender: function (info, test) {
//                        var room_capacity = document.createElement('strong');
//                        room_capacity.innerText = ' (' + info.capacity + ')';
//                        room_capacity.setAttribute('data-html', 'true');
//                        room_capacity.setAttribute('class', 'my_tooltip');
//                        test.find('.fc-cell-text')[0].appendChild(room_capacity);
//
//                        var popover = new Popover(room_capacity, {
//                            animation: true,
//                            delay: 200,
//                            title: info.title,
//                            content: info.description,
//                            trigger: 'hover',
//                            html: true
//                        });
//                    },
//
//                    /*SELECT EVENT ON VIEW CLICK*/
//                    select: function (start, end, jsEvent, view, resource) {
//                        var branch_id = false
//                        rpc.query({
//                            model: 'res.users',
//                            method: 'get_current_branch',
//                            args: [[]]
//                        }).then(function (res) {
//                            branch_id = res
//                            if (branch_id){
//                                var current_time = moment().format('YYYY-MM-DD HH:mm:ss')
//                                var start_date = moment(start).format('YYYY-MM-DD HH:mm:ss')
//                                var end_date = moment(end).format('YYYY-MM-DD HH:mm:ss')
//                                var resourceId = resource.id;
//                                var dialog = new dialogs.FormViewDialog(self, {
//                                    res_model: 'walk.in.detail',
//                                    res_id: false,
//                                    title: _t("Walk In"),
//                                    readonly: false,
//                                    context: {
//                                        'default_room_floor_id': resource.floor,
//                                        'default_room_type_id': resource.type,
//                                        'default_room_id': parseInt(resource.id),
//                                        'default_arrival_date': start_date,
//                                        'default_departure_date': end_date,
//                                        'default_branch_id': parseInt(branch_id)
//                                    },
//                                    on_saved: function (record, changed) {
//                                        $('#backend_resource_view').fullCalendar('destroy');
//                                        self.prepareResourceView(moment_date)
//                                        $('.fc-divider').find('.fc-cell-content').addClass('fc-expander');
//                                    },
//                                }).open();
//                            }
//                        });
//                    },
//
//                    selectAllow: function (selectInfo) {
//                        if (selectInfo.start.isBefore(moment().subtract(1, 'd').toDate()))
//                            return false;
//                        return true;
//                    },
//
//                    viewRender: function (view) {
//                        if (view.type && view.type == "week") {
//                            $('.fc-divider').find('.fc-cell-content').addClass('fc-expander');
//                        }
//
//                        $('.color-div .add-color').empty()
//                        $('.fc-center').empty()
//                        for (var index in color_dict) {
//                            $('.fc-center').append('<span id="' + color_dict[index] + '" style="width: 42px;height: 15px;display: inline-flex;margin-right: 5px;background-color:' + color_dict[index] + '"></span><span style="margin-right: 10px;font-size: 15px;">' + index + '</span>');
//                        }
//                        $('.title-display').html(view.title)
//                        self.get_title = view.title
//                    },
//                });
//                    if (!moment_date){
//                        var input = `<input type="text" id="select_date" class="datepicker" style="display:none;"/>`
//                        var span_tag = `<span class="title-display">` + self.get_title + `</span>`
//                        $(document).find('.fc-left').append(span_tag);
//                        $(document).find('.fc-left').append(input);
//                    }
//                    $("#select_date").datepicker({
//                    showOn: "button",
//                    buttonText: "<i class='fa fa-calendar'></i>",
//                    beforeShowDay: function (date) {
//                        if (self.highlight_dates) {
//                            var month = date.getMonth() + 1;
//                            var year = date.getFullYear();
//                            var day = date.getDate();
//                            var newdate = day + "-" + month + '-' + year;
//                            var tooltip_text = "New event on " + newdate;
//                            if ($.inArray(newdate, self.highlight_dates) != -1) {
//                                return [true, "highlight", tooltip_text];
//                            }
//                            return [true];
//                        }
//                    },
//                    onSelect: function(dateText) {
//                        $('#backend_resource_view').fullCalendar('gotoDate', moment(dateText).format('YYYY-MM-DD'));
//                        $('.title-display').html(self.get_title)
//                    }
//                });
//                }, 200)
//            })
//            }, 100)
//        },
//
//        next_prev_today_BtnClick: function () {
//            var self = this;
//            var date = moment($('#backend_resource_view').fullCalendar('getDate')).format('YYYY-MM-DD');
//            $('#backend_resource_view').fullCalendar('destroy');
//            self.prepareResourceView(date);
//            $('.fc-divider').find('.fc-cell-content').addClass('fc-expander');
//        },
//
//        changed: function (e) {
//            var nval = this.$(".o_searchview_extended_prop_field").val();
//            if(this.attrs.selected === null || this.attrs.selected === undefined || nval != this.attrs.selected.name) {
//                this.select_field(_.detect(this.fields, function (x) {return x.name == nval;}));
//            }
//        },
//
//        operator_changed: function (e) {
//            this.value.show_inputs($(e.target));
//        },
//        /**
//         * Selects the provided field object
//         *
//         * @param field a field descriptor object (as returned by fields_get, augmented by the field name)
//         */
//        select_field: function (field) {
//            var self = this;
//            if(this.attrs.selected !== null && this.attrs.selected !== undefined) {
//                this.value.destroy();
//                this.value = null;
//                this.$('.o_searchview_extended_prop_op').html('');
//            }
//            this.attrs.selected = field;
//            if(field === null || field === undefined) {
//                return;
//            }
//
//            var type = field.type;
//            var Field = core.search_filters_registry.getAny([type, "char"]);
//
//            this.value = new Field(this, field);
//            _.each(this.value.operators, function (operator) {
//                $('<option>', {value: operator.value})
//                    .text(String(operator.text))
//                    .appendTo(self.$('.o_searchview_extended_prop_op'));
//            });
//            var $value_loc = this.$('.o_searchview_extended_prop_value').show().empty();
//            this.value.appendTo($value_loc);
//        },
//
//        load_partners: function (query) {
//            var self = this;
//            var loaded_partners = [];
//            rpc.query({
//                model: 'res.partner',
//                method: 'search_read',
//                fields: ['name'],
//                domain: ['|', '|', ['name', 'ilike', query],
//                    ['mobile', 'ilike', query],
//                    ['email', 'ilike', query]
//                ],
//                limit: 7,
//            }, {
//                async: false
//            }).then(function (partners) {
//                loaded_partners = partners
//            });
//            return loaded_partners;
//        },
//    });
//    core.action_registry.add('tag_resource_view', ResourceView);
//    return ResourceView;
//});
