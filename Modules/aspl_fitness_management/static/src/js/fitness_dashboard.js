odoo.define('aspl_fitness_management.fitness_dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');
var QWeb = core.qweb;
var web_client = require('web.web_client');
var utils = require('web.utils');
var ajax = require('web.ajax');

var FitnessDashboard = AbstractAction.extend({

    template: 'FitnessDashboardMain',

        events: {
            'click .total_members':'total_members',
            'click .membership_history': 'membership_history',
            'click .subscriber_plan': 'subscriber_plan',
            'click .service': 'service',
            'click .to_expire_plan': 'to_expire_plan',
            'click .payment_button': 'payment_button',
            'click .monthly_chart': 'monthly_chart',
            'click .yearly_chart': 'yearly_chart',
            'click .male_chart': 'male_chart',
            'click .female_chart': 'female_chart',
        },

        init: function(parent, context) {
            this._super(parent, context);
        },

    willStart: function(){
        var self = this;
        return this._super()
        .then(async function() {
            var members =  self._rpc({
                    model: 'res.partner',
                    method: 'get_fitness_data',
            }).then(function(result) {
                if (result){
                    $('.total_members_data')[0].innerHTML = result.total_members;
                    $('.membership_history_data')[0].innerHTML = result.membership_history;
                    $('.subscriber_plan_data')[0].innerHTML = result.subscriber_plan;
                    $('.service_data')[0].innerHTML = result.product_ids;
                }
            });

            var expiry_count =  self._rpc({
                    model: 'subscriber.membership.history',
                    method: 'expiry_alert_count',
            }).then(function(result) {
                if (result){
                    $('.to_expire_plan_data')[0].innerHTML = result;
                }
            });

            var pending_membership =  self._rpc({
                    model: 'subscriber.membership.history',
                    method: 'payment_pending_membership',
            }).then(function(result) {
                if (result){
                    for(var data = 0; data < result.length; data++){
//                        console.log('result[data]>>>>>>>>', result[data])
                        var html = "<tr class='tr-body-content'>";
                        html += "<td class='col-3'><span>"+result[data].invoice_id[1]+"</span></td>";
                        html += "<td class='col-4'><span>"+result[data].membership_id[1]+"</span></td>";
                        html += "<td class='col-1'><span>"+result[data].currency_symbol+result[data].amount_due+"</span></td>";
                        html += "<td class='col-5'><button class='payment_button' value='"+result[data].id+"'>Pay Now</button></td>";
                        html += "</tr>";
                        $(".tbody-content").append(html);
                    }
                }
            });
        });
    },

    render_dashboard: async function() {
        var self = this;
        self.past_month_collection();
        var multi_branch = await ajax.jsonRpc('/check_multi_branch', 'call', {
            model: 'res.users', method: 'has_group',
            args: ['aspl_fitness_management.group_multi_branches'],
        });
        if (multi_branch){
            $('.bottom-widget-section')[0].style.display = "block";
            $('.fitness_dashboard_container')[0].style.overflow = "scroll";
        }
        else{
            $('.bottom-widget-section')[0].style.display = "none";
            $('.fitness_dashboard_container')[0].style.overflow = "initial";
        }
        self.$('.fitness_dashboard_container').append(QWeb.render('FitnessDashboardMain'));
    },

    render_graphs: function(){
        var self = this;
        self.sales_chart();
        self.branch_chart();
        self.branch_gender_chart();
    },

    monthly_chart: function() {
      var monthly = document.getElementById("monthly");
      var yearly = document.getElementById("yearly");
      var sales_chart_monthly = document.getElementById("sales_chart_monthly");
      var sales_chart_yearly = document.getElementById("sales_chart_yearly");
      sales_chart_monthly.style.display = "block";
      sales_chart_yearly.style.display = "none";
      monthly.checked = true;
      yearly.checked = false;
    },

    yearly_chart: function() {
      sales_chart_yearly.style.display = "block";
      sales_chart_monthly.style.display = "none";
      yearly.checked = true;
      monthly.checked = false;
    },


    male_chart: function() {
      var male = document.getElementById("male");
      var female = document.getElementById("female");
      var branch_gender_chart_male = document.getElementById("branch_gender_chart_male");
      var branch_gender_chart_female = document.getElementById("branch_gender_chart_female");
      branch_gender_chart_male.style.display = "block";
      branch_gender_chart_female.style.display = "none";
      male.checked = true;
      female.checked = false;
    },

    female_chart: function() {
      branch_gender_chart_female.style.display = "block";
      branch_gender_chart_male.style.display = "none";
      female.checked = true;
      male.checked = false;
    },

//  Total Members

    past_month_collection: async function() {
        var self = this;
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        var past_month_membership_collection = await self._rpc({
                    model: 'subscriber.membership.history',
                    method: 'past_month_collection',
            });
        var past_month_plan_collection = await self._rpc({
                    model: 'subscriber.plan',
                    method: 'past_month_collection',
            });
        let total_past_month_collection = past_month_membership_collection[0] + past_month_plan_collection;

        $('.last_30_days_data')[0].innerHTML = past_month_membership_collection[1]+ ' ' + total_past_month_collection;
    },


//  Total Members

    total_members: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        this.do_action('aspl_fitness_management.action_subscriber')
    },

//  Membership History

    membership_history: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        this.do_action('aspl_fitness_management.action_subscriber_membership_history')
    },

//  subscriber plan

    subscriber_plan: async function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        this.do_action('aspl_fitness_management.action_subscriber_gym_plan')
    },

//  services

    service: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        this.do_action('aspl_fitness_management.action_service_product')
    },

//  To expire plan

    to_expire_plan: async function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        var current_date = await self._rpc({
                    model: 'subscriber.membership.history',
                    method: 'current_date',
            });
        var expiry_alert_date = await self._rpc({
                    model: 'subscriber.membership.history',
                    method: 'expiry_alert_date',
            });
        this.do_action({
            name: "To Be Expire Memberships",
            type: 'ir.actions.act_window',
            res_model: 'subscriber.membership.history',
            view_mode: 'tree,form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['end_date','>=', current_date],['end_date','<=', expiry_alert_date]],
            target: 'current',
        }, options)
    },


    payment_button: async function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        let membership_id = e.target.value;
        var pending_membership = await self._rpc({
                    model: 'subscriber.membership.history',
                    method: 'search_read',
                    domain: [['id', '=', membership_id]],
            })

        this.do_action({
            name: 'Register Payment',
            type: 'ir.actions.act_window',
            res_model: 'account.payment.register',
            view_mode: 'form',
            views: [[false, 'form']],
            // view_id: ir_view_id,
            target: 'new',
            context: {'default_invoice_ids': [(4, pending_membership[0].invoice_id[0], null)],
                        'active_model': 'account.move',
                        'active_ids': [pending_membership[0].invoice_id[0]],
                        'membership_id': pending_membership[0].id,
                        },
        }, options)
    },


    sales_chart: function() {
        var self = this;
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        $(function() {
            async function lineGraph() {
                var monthly_membership_collection = await self._rpc({
                            model: 'subscriber.membership.history',
                            method: 'month_wise_collection',
                    });
                var monthly_plan_collection = await self._rpc({
                            model: 'subscriber.plan',
                            method: 'month_wise_collection',
                    });
                let yearly_membership_collection_total = monthly_membership_collection[0].reduce((a, b) => a + b, 0)
                let yearly_plan_collection_total = monthly_plan_collection.reduce((a, b) => a + b, 0)
                var total_yearly_collection = yearly_membership_collection_total + yearly_plan_collection_total
                $('.yearly_collection_data')[0].innerHTML = monthly_membership_collection[1] +' '+ total_yearly_collection;
                var sales_chart_monthly = document.getElementById("sales_chart_monthly");
                if(sales_chart_monthly.getContext) {
                    var sales_context_monthly = sales_chart_monthly.getContext("2d");
                    var xValues = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];

                    var sale_chart_monthly = new Chart(sales_context_monthly, {
                        type: "line",
                        data: {
                        labels: xValues,
                        datasets: [{
                              label: "Membership",
                              data: monthly_membership_collection,
                              borderColor: "#c6f0a1",
                              fill: false
                            }, {
                              label: "Plans",
                              data: monthly_plan_collection,
                              borderColor: "#239fc1",
                              fill: false
                            }]
                        },
                        options: {
                        legend: {display: true, position: 'bottom'},
                            title: {
                                display: true,
                                text: "Monthly Collection of Membership and Plans"
                            }
                        }
                    });
                }
                var yearly_membership_collection = await self._rpc({
                            model: 'subscriber.membership.history',
                            method: 'year_wise_collection',
                    });
                var yearly_plan_collection = await self._rpc({
                            model: 'subscriber.plan',
                            method: 'year_wise_collection',
                    });
                var sales_chart_yearly = document.getElementById("sales_chart_yearly");
                if(sales_chart_yearly.getContext) {
                    var sales_context_yearly = sales_chart_yearly.getContext("2d");
                    let years = []
                    let currentyear = new Date().getFullYear();
                    for(var num = 0;num < 5; num++){
                        years.unshift(currentyear - num);
                    }
                    var xValues = years;
                    var sale_chart_yearly = new Chart(sales_context_yearly, {
                        type: "line",
                        data: {
                        labels: xValues,
                        datasets: [{
                              label: "Membership",
                              data: yearly_membership_collection,
                              borderColor: "#c6f0a1",
                              fill: false
                            }, {
                                label: "Plans",
                                data: yearly_plan_collection,
                                borderColor: "#239fc1",
                                fill: false
                            }]
                        },
                        options: {
                            legend: {display: true, position: 'bottom'},
                            title: {
                                display: true,
                                text: "Last 5 Year Collection of Membership and Plans"
                            }
                        }
                    });
                }
            self.monthly_chart();
            }
            lineGraph();
        });
    },

    branch_chart: function() {
        var self = this;
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        $(function() {
            async function lineGraph() {
                var branch_data = await self._rpc({
                            model: 'company.branch',
                            method: 'get_allowed_branch_data',
                    });
                let branch_names = branch_data.map(a => a.name);
                var membership_users_by_branch = await self._rpc({
                            model: 'subscriber.membership.history',
                            method: 'user_by_branch',
                    });
                var plan_users_by_branch = await self._rpc({
                            model: 'subscriber.plan',
                            method: 'user_by_branch',
                    });
                var branch_chart = document.getElementById("branch_chart");
                if(branch_chart.getContext) {
                    var branch_context = branch_chart.getContext("2d");
                    var xValues = branch_names;
                    var bar_chart = new Chart(branch_context, {
                        type: "bar",
                        data: {
                        labels: xValues,
                        datasets: [{
                                label: "Membership",
                                data: membership_users_by_branch,
                                backgroundColor: "#e8c3b9",
                                fill: false
                            }, {
                                label: "Plans",
                                data: plan_users_by_branch,
                                backgroundColor: "#00aba9",
                                fill: false
                            }]
                        },
                        options: {
                            legend: {display: true, position: 'bottom'},
                            scales: {
                                yAxes: [{
                                    ticks: {
                                        beginAtZero: true
                                    }
                                }]
                            },
                            title: {
                                display: true,
                                text: "Branch Progress Ratio"
                            }
                        }
                    });
                }
            }
            lineGraph();
        });
    },

    branch_gender_chart: function() {
        var self = this;
        var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        $(function() {
            async function pieGraph() {
                var total_branch_gender = await self._rpc({
                            model: 'company.branch',
                            method: 'get_allowed_branch_data',
                    });
                let branch_gender_names = total_branch_gender.map(a => a.name);
                var membership_users_by_branch_male = await self._rpc({
                            model: 'subscriber.membership.history',
                            method: 'user_by_branch_male',
                    });
                var membership_users_by_branch_female = await self._rpc({
                            model: 'subscriber.membership.history',
                            method: 'user_by_branch_female',
                    });
                var branch_gender_chart_male = document.getElementById("branch_gender_chart_male");
                if(branch_gender_chart_male.getContext) {
                    var branch_gender_male_context = branch_gender_chart_male.getContext("2d");
                    var xValues = branch_gender_names;
                    var backgroundColorcodes = []
                    for(var num = 0;num < xValues.length; num++){
                        var randomColor = Math.floor(Math.random()*16777215).toString(16);
                        backgroundColorcodes.push("#"+randomColor);
                    }
                    var bar_chart = new Chart(branch_gender_male_context, {
                        type: "pie",
                        data: {
                            labels: xValues,
                            datasets: [{
                                    label: "Male",
                                    data: membership_users_by_branch_male,
                                    backgroundColor: backgroundColorcodes,
                                },]
                        },
                        options: {
                            legend: {display: true, position: 'bottom'},
                        }
                    });
                }
                var branch_gender_chart_female = document.getElementById("branch_gender_chart_female");
                if(branch_gender_chart_female.getContext) {
                    var branch_gender_female_context = branch_gender_chart_female.getContext("2d");
                    var xValues = branch_gender_names;
                    var backgroundColorcodes = []
                    for(var num = 0;num < xValues.length; num++){
                        var randomColor = Math.floor(Math.random()*16777215).toString(16);
                        backgroundColorcodes.push("#"+randomColor);
                    }
                    var bar_chart = new Chart(branch_gender_female_context, {
                        type: "pie",
                        data: {
                            labels: xValues,
                            datasets: [{
                                label: "Female",
                                data: membership_users_by_branch_female,
                                backgroundColor: backgroundColorcodes,
                            },]
                        },
                        options: {
                            legend: {display: true, position: 'bottom'},
                        }
                    });
                }
            self.male_chart();
            }
            pieGraph();
        });
    },

    start: function() {
        var self = this;
        return this._super().then(function() {
            self.render_dashboard();
            self.render_graphs();
        });
    },
    });

    core.action_registry.add('fitness_dashboard', FitnessDashboard);

    return  { FitnessDashboard:  FitnessDashboard };

});
