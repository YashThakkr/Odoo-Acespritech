/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
publicWidget.registry.WebsitePickup = publicWidget.Widget.extend({
    selector: "#o_wsale_products_main_row",
    
    init() {
        this._super.apply(this, arguments);
        if($('.ac-row-data-list').length <= 1){
            $(document).find('.confirm_order_to_deliver').hide();
        }
    },
    events: {
        "click .table-add": "Addtable",
        "input .ac_product_name": "search_product",
        "click .table-remove": "RemoveProductLine",
        "click .confirm_order_to_deliver": "ConfirmOrder",
        "change .ac_product_qty": "ChangeProductQty",
    },

    async get_currency(){
        const currency = await this.rpc("/get-cuurency-symbol", {})
        return currency[0].currency
    },

    
    onchange_product :function (currency){
        var untax_amount = 0.0
        var taxes = 0.0
        var elements = document.querySelectorAll('.ac-row-data-list.show_tr');
        elements.forEach(function (element) {
            untax_amount = untax_amount + parseFloat($(element).find('.ac_product_total_price').html());
            taxes = taxes + parseFloat($(element).find('.ac_product_tax').html())
        });
        $('.ac_product_subtotal').html(untax_amount.toFixed(2)+' '+currency);
        $('.ac_product_taxes').html(taxes.toFixed(2)+' '+currency);
        $('.ac_product_all_total').html(((parseFloat($('.ac_product_subtotal').html()))+(parseFloat($('.ac_product_taxes').html()))).toFixed(2)+' '+currency);
    },
    RemoveProductLine(event) {
        var target = $(event.currentTarget);
        target.parents('tr').detach();
        var cuurency = ''
        var self = this
        this.rpc("/get-cuurency-symbol", {}).then(function(res){
            self.onchange_product(res[0].currency);
            if($('.ac-row-data-list').length <= 1){
              $(document).find('.confirm_order_to_deliver').hide();
          }
        }) 
        
      },
    Addtable(e) {
        var $TABLE = $('#table_quick_view');
        var $clone = $('#table_quick_view').find('tr.d-none').clone(true).removeClass('d-none table-line').addClass('show_tr');
        var length_tr=$TABLE.find('table').find('.ac_product_name').length
        var temp = 0
        $TABLE.find('.show_tr').find('.ac_product_name').each(function(){
                if($(this).val() == '' && length_tr < 2){
                    $TABLE.find('table').append($clone).find('.ac_product_name').focus();
                    temp = 2
                }else{
                    if($(this).attr('product-id') == ''){
                        temp = 1;
                    }else{

                        temp = 0;
                    }
                }
            });
            if(temp == 0){
                if($TABLE.find('.show_tr .ac_product_name').html() != ''){
                    $(document).find('.confirm_order_to_deliver').show();
                }
                $TABLE.find('.show_tr .ac_product_name').attr('disabled','disabled');
                $TABLE.find('table').append($clone).find('.ac_product_name').focus();
            }
    },


    ChangeProductQty(event){
        this.rpc("/get-cuurency-symbol", {}).then(function(res){
            var currency =res[0].currency
            var currentTarget = $(event.currentTarget);
            var qty = currentTarget.val();
            var elements = document.querySelectorAll('.ac-row-data-list.show_tr');
            if(qty != 0){
                    currentTarget.parent().parent().parent().find(".ac_product_tax").html((parseFloat(qty)*parseFloat(currentTarget.parent().parent().parent().find(".product_tax").html())).toFixed(2) +' '+currency);
                    currentTarget.parent().parent().parent().find(".ac_product_total_price").html((parseFloat(qty)*parseFloat(currentTarget.parent().parent().parent().find('.ac_product_unit_price').html())).toFixed(2) +' '+currency);
                    var untax_amount = 0.0
                    var taxes = 0.0
                    elements.forEach(function (element) {
                        untax_amount = untax_amount + parseFloat($(element).find(".ac_product_total_price").html())
                        taxes = taxes + parseFloat($(element).find(".ac_product_tax").html())
                    });
                    $('.ac_product_subtotal').html(untax_amount.toFixed(2)+' '+currency);
                    $('.ac_product_taxes').html(taxes.toFixed(2)+' '+currency);
                    $('.ac_product_all_total').html(((parseFloat($('.ac_product_subtotal').html()))+(parseFloat($('.ac_product_taxes').html()))).toFixed(2)+' '+currency);
                }
                else{
                    currentTarget.parent().parent().parent().find(".ac_product_tax").html((parseFloat(qty)*parseFloat($(this).parent().parent().parent().find(".product_tax").html())).toFixed(2) +' '+currency);
                    currentTarget.parent().parent().parent().find(".ac_product_total_price").html((parseFloat(qty)*parseFloat($(this).parent().parent().parent().find(".ac_product_unit_price").html())).toFixed(2) +' '+currency);
                    var untax_amount = 0.0
                    var taxes = 0.0
                    elements.forEach(function (element) {
                        untax_amount = untax_amount + parseFloat($(element).find(".ac_product_total_price").html())
                        taxes = taxes + parseFloat($(element).find(".ac_product_tax").html())
                    });
                    $('.ac_product_subtotal').html(untax_amount.toFixed(2)+' '+currency);
                    $('.ac_product_taxes').html(taxes.toFixed(2)+' '+currency);
                    $('.ac_product_all_total').html(((parseFloat($('.ac_product_subtotal').html()))+(parseFloat($('.ac_product_taxes').html()))).toFixed(2)+' '+currency);
                    currentTarget.parents('tr').detach();
                }
            
        }) 
        
    },
    
    search_product(event) {
        var target = $(event.currentTarget);
        if(event.which == 13){
            $('.table-add').trigger('click');
            $('.ui-autocomplete').css('display','none');
        }
        if($(".ac_product_name").val() == ''){
            target.find(".ac_product_unit_price").html('');
            target.find(".ac_product_total_price").html('');
            $(target).parent().parent().find('.ac_product_qty').val('1');
        }
        var self = this
        var product_name = $(event.target)[0].value;
        var product_id = 0;
        var ac_list_of_products = [];
        var currency = ''
        var list_of_products = [];
        var availableTags = [];
        this.rpc = this.bindService("rpc");
        this.rpc("/get-product-list", { search_string: product_name,
            })
            .then(function (res) {
                    if(res != undefined){
                        ac_list_of_products = res;
                        for(var rec in res){
                            availableTags.push({label: res[rec].name,value: res[rec].name, id: res[rec].id});
                        }
                            target.autocomplete({
                                source: availableTags,
                                delay:400,
                                select: function(event, ui) {
                                    var ac_product_id = ui.item.id;
                                        for(var each=0;each<ac_list_of_products.length;each++){
                                            if(ac_list_of_products[each].id == ac_product_id){
                                                list_of_products.push(ac_list_of_products[each]);
                                                $(this).parent().parent().find(".ac_product_name").val(ac_list_of_products[each].name);
                                                $(this).parent().parent().find(".ac_product_name").attr("product-id",ac_list_of_products[each].id);
                                                $(this).parent().parent().find(".ac_product_unit_price").html(ac_list_of_products[each].list_price.toFixed(2)+' '+ac_list_of_products[each].currency);
                                                $(this).parent().parent().find(".ac_product_tax").html(ac_list_of_products[each].tax_total.toFixed(2)+' '+ac_list_of_products[each].currency);
                                                $(this).parent().parent().find(".product_tax").html(ac_list_of_products[each].tax_total.toFixed(2)+' '+ac_list_of_products[each].currency);
                                                $(this).parent().parent().find(".ac_product_total_price").html((parseFloat(ac_list_of_products[each].list_price).toFixed(2))+' '+ac_list_of_products[each].currency);
                                                
                                                self.rpc("/get-cuurency-symbol", {}).then(function(res){
                                                    self.onchange_product(res[0].currency);
                                                })                                                
                                            }
                                        }
                                }
                            }).bind('focus', function(){ $(this).autocomplete("search"); } );
                        target.trigger("focus");
                        }
                    });
            
    },

    ConfirmOrder(e){
        var list_of_input = $(".add_row_table").find('input');
        var allow_create_line = true;
        var list_of_cart_value = []
        var elements = document.querySelectorAll('.ac-row-data-list.show_tr');
            elements.forEach(function (element) {
                var qty =$(element).find('.ac_product_qty').val();
                var product_id = $(element).find(".ac_product_name").attr("product-id")
                list_of_cart_value.push({'product_id':product_id,'qty':qty});
            })
        if(list_of_cart_value){
            this.rpc("/listcart/update",{'product_list':list_of_cart_value})
                .then(function (data) {
                    window.location.replace("/shop/cart");
            });
        }
        else{
            alert("Order line is Empty !!!")
        }
    }
});