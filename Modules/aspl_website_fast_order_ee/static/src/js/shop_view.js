/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import wSaleUtils from "@website_sale/js/website_sale_utils";
import publicWidget from "@web/legacy/js/public/public_widget";
import { Component } from '@odoo/owl';

var currency = ''
var list_of_products = [];
var ac_list_of_products = [];
var availableTags = [];
    publicWidget.registry.WebsitePickup = publicWidget.Widget.extend({
        selector: "#website_fast_order",
        init() {
            if($(".ac_product_name").length !=0){
                this.rpc = this.bindService("rpc");
                this.rpc("/get-product-list", {},
                $.blockUI({
                    fadeIn : 700,
                    fadeOut: 1000,
                    centerY: false,
                    showOverlay: true,
                    message: $('<img src="/aspl_website_fast_order_ee/static/description/loading-icon.gif"/>') }),{async:true})
                .then(function (res) {
                if (res != undefined) {
                    ac_list_of_products = res;
                    for (var i in res) {
                        availableTags.push({label: res[i].name, value: res[i].name, id: res[i].id});
                    }
                    $.unblockUI();
                }
            });
            }
            if (typeof($(this).find('.col-md-12.quick_list_view').html()) != 'undefined') {
                $('.products_pager').hide();
            } else {
                $('.products_pager').show();
            }
            if ($('.ac-row-data-list').length <= 1) {
                $(document).find('.confirm_order_to_deliver').hide();
            }
            this._super.apply(this, arguments);
        },

        events: {
            "click .qty-plus": "AddProductQty",
            "click .qty-min": "RemoveProductQty",
            "click .table-add": "AddProductSelection",
            "click .table-remove": "RemoveProductLine",
            "click .confirm_order_to_deliver": "ConfirmOrderToDeliver",
            "input .ac_product_name": "AcProductChange",
            "change .ac_product_qty": "AcProductQty",
            "show.bs.collapse #accordion": "ActivePanelHeading",
            "hide.bs.collapse #accordion": "HidePanelHeading",
            "hidden.bs.collapse .panel-group": "toggleIcon",
            "shown.bs.collapse .panel-group": "toggleIcon",
            'change select[name="file_type"]': '_onSelectChange',
            'change #csv_file': '_onChangeCSV',
            'change #xls_file': '_onChangeXLS',
            'click .add_product': 'AddProducts',
        },

        AddProducts(e) {
            var $input = $(e.currentTarget);
            var product_id = e.currentTarget.attributes.getNamedItem('data-product-id').value
            var value = $("#"+product_id)[0].value
            var line_id = parseInt($input[0].attributes.line_id.value, 10);
            this.rpc = this.bindService("rpc");
            this.rpc("/shop/cart/update_json", { line_id: line_id,
                product_id: parseInt(product_id),
                add_qty: value})
                .then(function (data) {
                $input[0].attributes.line_id.value = data.line_id;
                sessionStorage.setItem('website_sale_cart_quantity', data.cart_quantity);
                wSaleUtils.updateCartNavBar(data);
                wSaleUtils.showWarning(data.warning);
                // Propagating the change to the express checkout forms
                // core.bus.trigger('cart_amount_changed', data.amount, data.minor_amount);
                Component.env.bus.trigger('cart_amount_changed', [data.amount, data.minor_amount]);
            });
        },

        ActivePanelHeading(e) {
            $(e.target).prev('.panel-heading').addClass('active');
        },

        HidePanelHeading(e) {
            $(e.target).prev('.panel-heading').removeClass('active');
        },

        _onSelectChange(e) {
            if ($(e.currentTarget).val() == 'csv') {
                $('#csv_file').css('display', 'block');
                $('#xls_file').css('display', 'none');
            } else {
                $('#xls_file').css('display', 'block');
                $('#csv_file').css('display', 'none');
            }
        },

        _onChangeCSV(e) {
            var validExts = new Array(".csv");
            var fileExt = e.currentTarget.value;
            fileExt = fileExt.substring(fileExt.lastIndexOf('.'));
            if (validExts.indexOf(fileExt) < 0) {
                alert("Invalid file selected, valid files are of " +
                    validExts.toString() + " types.");
                $(e.currentTarget).val('');
                return false;
            }
            else return true;
        },

        _onChangeXLS(e) {
            var validExts = new Array(".xlsx", ".xls");
            var fileExt = e.currentTarget.value;
            fileExt = fileExt.substring(fileExt.lastIndexOf('.'));
            if (validExts.indexOf(fileExt) < 0) {
                alert("Invalid file selected, valid files are of " +
                    validExts.toString() + " types.");
                $(e.currentTarget).val('');
                return false;
            }
            else return true;
        },

        ConfirmOrderToDeliver(e) {
            var list_of_input = $(".add_row_table").find('input');
            var allow_create_line = true;
            var list_of_cart_value = []
            $(".ac-row-data-list").each(function () {
                var qty = $(this).find(".ac_product_qty").val();
                var product_id = $(this).find(".ac_product_name").attr("product-id");
                list_of_cart_value.push({'product_id': product_id, 'qty': qty});
            });
            console.log('-------------->list_of_cart_value',list_of_cart_value)
            if (list_of_cart_value) {
                this.rpc = this.bindService("rpc");
                this.rpc("/listcart/update", {'product_list': list_of_cart_value})
                .then(function (data) {
                    window.location.replace("/shop/cart");
                });
                // ajax.jsonRpc("/listcart/update", 'call', {'product_list': list_of_cart_value})
            } else {
                alert("Order line is Empty !!!")
            }
        },


        AcProductQty(e) {
            var self = this;
            var qty = parseInt($(e.currentTarget).val());
            if (qty != 0) {
                $(e.currentTarget).parent().parent().parent().find(".ac_product_tax").html((parseFloat(qty) * parseFloat($(e.currentTarget).parent().parent().parent().find(".product_tax").html())).toFixed(2) + ' ' + currency);
                $(e.currentTarget).parent().parent().parent().find(".ac_product_total_price").html((parseFloat(qty) * parseFloat($(e.currentTarget).parent().parent().parent().find(".ac_product_unit_price").html())).toFixed(2) + ' ' + currency);
                var untax_amount = 0.0
                var taxes = 0.0
                $('.ac-row-data-list').each(function () {
                    untax_amount = untax_amount + parseFloat($(this).find('.ac_product_total_price').html())
                    taxes = taxes + parseFloat($(this).find('.ac_product_tax').html())
                });
                $('.ac_product_subtotal').html(untax_amount.toFixed(2) + ' ' + currency);
                $('.ac_product_taxes').html(taxes.toFixed(2) + ' ' + currency);
                $('.ac_product_all_total').html(((parseFloat($('.ac_product_subtotal').html())) + (parseFloat($('.ac_product_taxes').html()))).toFixed(2) + ' ' + currency);
            } else {
                $(e.currentTarget).parent().parent().parent().find(".ac_product_tax").html((parseFloat(qty) * parseFloat($(e.currentTarget).parent().parent().parent().find(".product_tax").html())).toFixed(2) + ' ' + currency);
                $(e.currentTarget).parent().parent().parent().find(".ac_product_total_price").html((parseFloat(qty) * parseFloat($(e.currentTarget).parent().parent().parent().find(".ac_product_unit_price").html())).toFixed(2) + ' ' + currency);
                var untax_amount = 0.0
                var taxes = 0.0
                $('.ac-row-data-list').each(function () {
                    untax_amount = untax_amount + parseFloat($(e.currentTarget).find('.ac_product_total_price').html())
                    taxes = taxes + parseFloat($(e.currentTarget).find('.ac_product_tax').html())
                });
                $('.ac_product_subtotal').html(untax_amount.toFixed(2) + ' ' + currency);
                $('.ac_product_taxes').html(taxes.toFixed(2) + ' ' + currency);
                $('.ac_product_all_total').html(((parseFloat($('.ac_product_subtotal').html())) + (parseFloat($('.ac_product_taxes').html()))).toFixed(2) + ' ' + currency);
                $(e.currentTarget).parents('tr').detach();
                self.onchange_product()
            }
        },

        AddProductQty(e) {
            var qty = parseInt($(e.currentTarget).parent().find('.ac_product_qty').val());
            $(e.currentTarget).parent().find('.ac_product_qty').val(qty + 1);
            $(e.currentTarget).parent().find('.ac_product_qty').trigger('change')
        },

        RemoveProductQty(e) {
            var qty = parseInt($(e.currentTarget).parent().find('.ac_product_qty').val());
            if (qty != 1) {
                $(e.currentTarget).parent().find('.ac_product_qty').val(qty - 1);
                $(e.currentTarget).parent().find('.ac_product_qty').trigger('change')
            }
        },

        AddProductSelection(e) {
        $('.confirm_order_to_deliver').show();
            var $TABLE = $('#table_quick_view');
            var $clone = $TABLE.find('tr.hide').clone(true).removeClass('hide table-line').addClass('show_tr');
            var length_tr = $TABLE.find('table').find('.ac_product_name').length
            var temp = 0
            $TABLE.find('.show_tr').find('.ac_product_name').each(function (event) {
                if ($(event.currentTarget).val() == '' && length_tr < 2) {
                    $TABLE.find('table').append($clone).find('.ac_product_name').focus();
                    temp = 2
                } else {
                    if ($(event.currentTarget).attr('product-id') == '') {
                        temp = 1;
                    } else {

                        temp = 0;
                    }
                }
            });
            if (temp == 0) {
                if ($('#table_quick_view').find('tbody tr.show_tr .ac_product_name').html() != '') {
                    $(e.currentTarget).find('.confirm_order_to_deliver').show();
                }
                $TABLE.find('.show_tr .ac_product_name').attr('disabled', 'disabled');
                $TABLE.find('table').append($clone).find('.ac_product_name').focus();
            }
        },

        RemoveProductLine(e) {
            var self = this;
            $(e.currentTarget).parents('tr').detach();
            self.onchange_product();
            if ($('.ac-row-data-list').length <= 1) {
                $(this).find('.confirm_order_to_deliver').hide();
            }
        },

        toggleIcon(e) {
            $(e.target)
                .prev('.panel-heading')
                .find(".more-less")
                .toggleClass('fa-plus fa-minus');
        },

        onchange_product(e) {
            var untax_amount = 0.0
            var taxes = 0.0
            $('.ac-row-data-list').each(function () {
                untax_amount = untax_amount + parseFloat($(this).find('.ac_product_total_price').html())
                taxes = taxes + parseFloat($(this).find('.ac_product_tax').html())
            });
            $('.ac_product_subtotal').html(untax_amount.toFixed(2) + ' ' + currency);
            $('.ac_product_taxes').html(taxes.toFixed(2) + ' ' + currency);
            $('.ac_product_all_total').html(((parseFloat($('.ac_product_subtotal').html())) + (parseFloat($('.ac_product_taxes').html()))).toFixed(2) + ' ' + currency);
        },

        AcProductChange(event) {
            if (event.which == 13) {
                $('.table-add').trigger('click');
                $('.ui-autocomplete').css('display', 'none');
            }
            if ($(event.currentTarget).val() == '') {
                $(event.currentTarget).parent().parent().find(".ac_product_unit_price").html('');
                $(event.currentTarget).parent().parent().find(".ac_product_total_price").html('');
                $(event.currentTarget).parent().parent().find(".ac_product_qty").val('1');
            }
            var self = this;
            var target = $(event.currentTarget);
            var product_name = $(event.target)[0].value;
            var product_id = 0;
            target.autocomplete({
                    source: availableTags,
                    delay: 0,
				    minLength:3,
                    select: function (eve, ui) {
                        var ac_product_id = ui.item.id;
                        target.attr("product-id", ac_product_id);
                        for (var i = 0; i < ac_list_of_products.length; i++) {
                            if (ac_list_of_products[i].id == ac_product_id) {
                                list_of_products.push(ac_list_of_products[i]);
                                $(this).parent().parent().find(".ac_product_name").val(ac_list_of_products[i].name);
                                $(this).parent().parent().find(".ac_product_qty").val(1);
                                $(this).parent().parent().find(".ac_product_name").attr("product-id", ac_list_of_products[i].id);
                                $(this).parent().parent().find(".ac_product_unit_price").html(ac_list_of_products[i].list_price.toFixed(2) + ' ' + ac_list_of_products[i].currency);
                                $(this).parent().parent().find(".product_img").html('<img class="image-circle" style="width:52px;height: 100%" src="data:image/jpeg;base64,' + ac_list_of_products[i].image + '" />');
                                $(this).parent().parent().find(".ac_product_tax").html(ac_list_of_products[i].tax_total.toFixed(2) + ' ' + ac_list_of_products[i].currency);
                                $(this).parent().parent().find(".product_tax").html(ac_list_of_products[i].tax_total.toFixed(2) + ' ' + ac_list_of_products[i].currency);
                                $(this).parent().parent().find(".ac_product_total_price").html((parseFloat(ac_list_of_products[i].list_price).toFixed(2)) + ' ' + ac_list_of_products[i].currency);
                                currency = ac_list_of_products[i].currency;
                                self.onchange_product();
                            }
                        }
                    }
                }).bind('focus', function () {
                    $(this).autocomplete("search");
                });
                target.trigger("focus");
        },

    });
// });