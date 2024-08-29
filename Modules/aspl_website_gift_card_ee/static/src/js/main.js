/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { registry } from "@web/core/registry";
import { whenReady } from "@odoo/owl";
import { jsonrpc } from "@web/core/network/rpc_service";

function notification(type, message){
    var types = ['success','warning','info', 'danger'];
    if($.inArray(type.toLowerCase(),types) != -1){
        $('div.span4').remove();
        var newMessage = '';
        switch(type){
        case 'success' :
        newMessage = '<i class="fa fa-check" aria-hidden="true"></i> '+message;
        break;
        case 'warning' :
        newMessage = '<i class="fa fa-exclamation-triangle" aria-hidden="true"></i> '+message;
        break;
        case 'info' :
        newMessage = '<i class="fa fa-info" aria-hidden="true"></i> '+message;
        break;
        case 'danger' :
        newMessage = '<i class="fa fa-ban" aria-hidden="true"></i> '+message;
        break;
        }
        $('body').append('<div class="span4 pull-right" style="width: 20%;position: absolute;top: 15%;right: 1%;">' +
                   '<div class="alert alert-'+type+' fade">' +
                   newMessage+
                  '</div>'+
                '</div>');
           $(document).find(".alert").css('opacity',1).show();
           $(document).find(".alert").delay(2000).addClass("in").fadeOut(10000);
    }
}

export function isNumeric(evt, element) {
    var charCode = (evt.which) ? evt.which : event.keyCode;
    if (charCode == 13) {
        return true
    }
    if (charCode != 8 && charCode != 0 && (charCode < 48 || charCode > 57) && charCode != 46) {
        $("#errmsg").html("Enter Digits Only !!!").show().fadeOut("slow");
        return false;
    }
}

publicWidget.registry.GiftCard = publicWidget.Widget.extend({
    selector: '#giftcard_pin_form, .gift_card_purchase, #gift_card_amount_pay, #SetPinModel, #addgiftcard, .oe_website_sale, #RechargeCardModel',

    willStart: function () {
        $('#giftcard_pin_form').validate({
            rules: {
                pin_no: {
                    required: true,
                    digits: true,
                },
                cfm_pin_no: {
                    required: true,
                    digits: true,
                    equalTo: "#pin_no"
                }
            }
        });
        this.rpc = this.bindService("rpc");
        return this._super.apply(this, arguments);
    },

    events: {
        'keypress #pin': 'PinKeyPress',
        'keypress #card_number': 'CardNumberKeyPress',
        'keypress #amount': 'GiftCardAmountPayKeyPress',
        'keypress #gift_qty': 'GiftQtyKeyPress',
        'keyup #gift_qty': 'KeyUpPressGiftQty',
        'keypress #pin_no': 'PinNoKeyPress',
        'keypress #cfm_pin_no': 'CfmPinNoKeyPress',
        'click #set_pin': 'OnclickSetPin',
        'click #set_pin_new': 'OnClickSetPinNew',
         'keydown #gift_card_apply_form input': 'KeyDownGiftCardApply',
         'keydown #gift_card_amount_pay input': 'KeyDownGiftCardAmountPay',
         'click #gift_card_pay': 'onclickGiftCardPay',
         'click #cancel_pay': 'onclickCancelPay',
         'click #gift_card_pay_form': 'onClickGiftCardPayForm',
         'click #gift_card_amount_pay_apply': 'onClickGiftCardAmountPayApply',
         'click #cancel_amount_pay': 'onClickCancelAmountPay',
         'keypress #recharge_amount': 'KeypressRechargeAmount',
         'click #recharge_submit': 'clickRechargeSubmit',
         'paste #recharge_amount': 'onPasteRechargeAmt',
    },

    PinKeyPress: function(ev){
         return isNumeric(ev.currentTarget.value, ev.currentTarget)
    },
    CardNumberKeyPress: function(ev){
        return isNumeric(ev.currentTarget.value, ev.currentTarget)
    },
    GiftCardAmountPayKeyPress: function(ev){
        var $this = $(ev.currentTarget);
        if ((event.which != 46 || $this.val().indexOf('.') != -1) &&
            ((event.which < 48 || event.which > 57) &&
            (event.which != 0 && event.which != 8))) {
            event.preventDefault();
        }

        var text = $(ev.currentTarget).val();
        if ((event.which == 46) && (text.indexOf('.') == -1)) {
            setTimeout(function() {
                if ($this.val().substring($this.val().indexOf('.')).length > 3) {
                    $this.val($this.val().substring(0, $this.val().indexOf('.') + 3));
                }
            }, 1);
        }

        if ((text.indexOf('.') != -1) &&
            (text.substring(text.indexOf('.')).length > 2) &&
            (event.which != 0 && event.which != 8) &&
            ($(ev.currentTarget)[0].selectionStart >= text.length - 2)) {
                event.preventDefault();
        }
        return isNumeric(ev.currentTarget.value, ev.currentTarget)
    },
    GiftQtyKeyPress: function(ev){
        return isNumeric(ev.currentTarget.value, ev.currentTarget)
    },
    KeyUpPressGiftQty: function(ev){
        ev.currentTarget.value = ev.currentTarget.value.replace(/[^0-9]/g, '');
    },
    PinNoKeyPress: function(ev){
        return isNumeric(ev.currentTarget.value, ev.currentTarget)
    },
    CfmPinNoKeyPress: function(ev){
        return isNumeric(ev.currentTarget.value, ev.currentTarget)
    },

    OnclickSetPin: function(e){
        var pin = $(e.currentTarget).parents('.modal-body').find("#pin_no").val();
        var confirmpin = $(e.currentTarget).parents('.modal-body').find("#cfm_pin_no").val();
        var card_id = $(e.currentTarget).parents('.modal-body').find("#card_id").val();
        if (pin && confirmpin) {
            if (pin != confirmpin) {
                e.preventDefault();
                $(e.currentTarget).parents('.modal-body').find("#error-set-pin").html("").html("Pin and confirm pin does not match");
                return false;
            } else {

                this.rpc("/shop/set/pin", {'card_id': card_id, 'pin': pin})
                .then(function (data) {
                    $('#SetPinModel').find("#pin_no").val('')
                    $('#SetPinModel').find("#cfm_pin_no").val('')
                    $('#SetPinModel').modal('hide');
                    notification('success','Successfully Pin Changed, Please login again..')
                    setTimeout(function(){
                    location.replace('/gift_card');
                    },3000)
                });
            }
        }
        else {
             $(e.currentTarget).parents('.modal-body').find("#pin_no").addClass('error-new');
             $(e.currentTarget).parents('.modal-body').find("#cfm_pin_no").addClass('error-new');
        }
      },
    OnClickSetPinNew: function(e){
        var pin = $("#pin_no").val();
        var confirmpin = $("#cfm_pin_no").val();
        if (pin && confirmpin) {
            if (pin != confirmpin) {
                $("#error-set-pin").html("").html("Pin and confirm pin does not match");
                return false;
            }
            else {
                e.preventDefault();
                $('#SetPinModel').modal('show');
                $("#close_pin_model").on('click', function () {
                    $('#giftcard_pin_form').submit();
                })
            }
        }
        else {
            $("#pin_no").addClass('error-new');
            $("#cfm_pin_no").addClass('error-new');
        }
      },
        KeyDownGiftCardApply: function(event){
            var keyCode = (event.keyCode ? event.keyCode : event.which);
            if (keyCode == 13) {
                $('#gift_card_pay_form').trigger('click');
            }
        },
        KeyDownGiftCardAmountPay: function(event){
            var keyCode = (event.keyCode ? event.keyCode : event.which);
            if (keyCode == 13) {
                $('#gift_card_amount_pay_apply').trigger('click');
            }
        },
        onclickGiftCardPay: function(ev){
            $("#addgiftcard").modal('show');
        },
        onclickCancelPay: function(ev){
            $("#addgiftcard").modal('hide');
            $('#gift_card_amount_pay input').val("");
            $('#gift_card_apply_form input').val("");
        },
        onClickGiftCardPayForm: function(e){
            e.preventDefault();
            var card_number = $('#card_number').val();
            var pin = $('#pin').val();
            if (card_number && pin) {
                this.rpc("/card_details", {'card_number': card_number, 'pin': pin})
                    .then(function (data) {
                        var data = JSON.parse(data);
                        if (data) {
                            $('#gift_card_apply_form').hide();
                            $('#gift_card_amount_pay').show();
                            $('#card_amount').val(data.balance);
                            $('#id').val(data.id);
                            $('#total_amount').val($('#total_amount').getAttributes('value')['value'])
                        }
                        else {
                            $("#error-gift-apply").html("").html("Wrong card number or pin");
                        }
                    });
            } else {
                $("#card_number").addClass('error-new');
                $("#pin").addClass('error-new');
                $("#error-gift-apply").html("").html("Enter card number or pin");
            }
        },
        onClickGiftCardAmountPayApply: function(ev){
            ev.stopPropagation();
            var id = $('#id').val();
            var amount = $('#amount').val();
            if (amount && amount < 1){
                alert('Minimum amount to redeem is 1');
                $("#amount").val("")
            }
            else{
                if (amount && id) {
                    this.rpc("/apply_gift_card", {'id': id, 'amount': amount})
                        .then(function (data) {
                            var data = JSON.parse(data);
                            if (data.success) {
                                if (data.url) {
                                    window.location.href = data.url;
                                }
                                else{
                                    location.reload();
                                }
                            } else if (data.error) {
                                $("#error-gift-amount").html("").html("You can not enter amount higher than total amount");
                            } else {
                                $("#error-gift-amount").html("").html("Not enough balance available");
                            }
                        });
                }
                else {
                    $("#amount").addClass('error-new');
                    $("#error-gift-amount").html("").html("Enter amount");
                }
            }
        },
        onClickCancelAmountPay: function(ev){
            $('#gift_card_amount_pay').hide();
            $('#gift_card_apply_form').show();
            $('#gift_card_amount_pay input').val("");
            $('#gift_card_apply_form input').val("");
            $("#addgiftcard").modal('hide');
        },
        KeypressRechargeAmount: function(ev){
            var $this = $(ev.currentTarget);
            if ((event.which != 46 || $this.val().indexOf('.') != -1) &&
                ((event.which < 48 || event.which > 57) &&
                (event.which != 0 && event.which != 8))) {
                event.preventDefault();
            }

            var text = $(ev.currentTarget).val();
            if ((event.which == 46) && (text.indexOf('.') == -1)) {
                setTimeout(function() {
                    if ($this.val().substring($this.val().indexOf('.')).length > 3) {
                        $this.val($this.val().substring(0, $this.val().indexOf('.') + 3));
                    }
                }, 1);
            }

            if ((text.indexOf('.') != -1) &&
                (text.substring(text.indexOf('.')).length > 2) &&
                (event.which != 0 && event.which != 8) &&
                ($(ev.currentTarget)[0].selectionStart >= text.length - 2)) {
                    event.preventDefault();
            }
            return isNumeric(ev.currentTarget.value, ev.currentTarget)
        },
        clickRechargeSubmit: function(ev){
            var id = $('#card_id').val();
            var amount = $('#recharge_amount').val();
            alert(amount)
            if (amount && amount < 1){
                alert('Minimum amount to recharge is 1');
                $("#recharge_amount").val("")
            }
            else{
                if (amount && id) {
                    this.rpc("/recharge_gift_card", {'id': id, 'amount': amount})
                        .then(function (data) {
                            if (data) {
                                location.replace('/shop/cart');
                            }

                        });
                }
                else {
                    $("#recharge_amount").addClass('error-new');
                    $("#error-recharge").html("").html("Enter Amount");
                }
            }
        },

        onPasteRechargeAmt: function(e){
            var text = e.originalEvent.clipboardData.getData('Text');
            if ($.isNumeric(text)) {
                if ((text.substring(text.indexOf('.')).length > 3) && (text.indexOf('.') > -1)) {
                    e.preventDefault();
                    $(this).val(text.substring(0, text.indexOf('.') + 3));
               }
            }
            else {
                e.preventDefault();
            }
        }
})

whenReady(() => {
    var applied_card = $('#applied_card');
    var applied_card_counter;
    var ajax = {};
    $(".js_add_cart_json").click(function (e) {
    var main_div=$(e.currentTarget).parent().parent()
    var product_id = main_div[0].getElementsByClassName('js_quantity')[0].getAttribute('data-product-id')
     jsonrpc("/check/product", {'product_id': product_id}).then(function (data) {
         if (data){
                setTimeout(function() {
                       notification("danger","You Can Not Modify This Product")
                },100);

            setTimeout(function() {

                }, 2000);
         }
        });
    });
    applied_card.on("mouseenter", function () {
        var self = this;
        clearTimeout(applied_card_counter);
        applied_card.not(self).popover('hide');
        applied_card_counter = setTimeout(function () {
            if ($(self).is(':hover') && !$(".mycart-popover:visible").length) {
                $.get("/shop/applied_card", {'type': 'popover'})
                    .then(function (data) {
                        applied_card.popover({
                            trigger: 'auto',
                            animation: true,
                            html: true,
                            title: function () {
                                return ("Applied Card");
                            },
                            container: 'body',
                            placement: 'auto',
                            content: data
                        })
//                           $(self).data("bs.popover").config.content = data;
                        $(self).popover("show");
                        $(".popover").on("mouseleave", function () {
                            $(self).trigger('mouseleave');
                        });
                    });
            }
        }, 100);

    }).on("mouseleave", function () {
        var self = this;
        setTimeout(function () {
            if (!$(".popover:hover").length) {
                if (!$(self).is(':hover')) {
                    $(self).popover('hide');
                }
            }
        }, 1000);
    }).on('shown.bs.popover', function(e) {
        var current_popover = '#' + $(e.target).attr('aria-describedby');
        var $cur_pop = $(current_popover);
        $cur_pop.find('.cancel_applied_gift_card').click(function(){
            var csrf = $(this).attr('data-csrf');
            var card_id = $(this).attr('data-card');
            var amount = $(this).attr('data-amount');
            jsonrpc("/cancel_gift_card", {'csrf':csrf,'card_id': card_id, 'amount': amount})
            .then(function (data) {
                if (data) {
                    location.replace('/shop/payment');
                }
            });
        });
    });

////    Table Pagination

    $.fn.pageMe = function(opts){
        var $this = this,
            defaults = {
                perPage: 7,
                showPrevNext: false,
                hidePageNumbers: false
            },
            settings = $.extend(defaults, opts);

        var listElement = $this;
        var perPage = settings.perPage;
        var children = listElement.children();
        var pager = $('.pager');

        if (typeof settings.childSelector!="undefined") {
            children = listElement.find(settings.childSelector);
        }

        if (typeof settings.pagerSelector!="undefined") {
            pager = $(settings.pagerSelector);
        }

        var numItems = children.length;
        var numPages = Math.ceil(numItems/perPage);

        pager.data("curr",0);

        if (settings.showPrevNext){
            $('<li><a href="#" class="prev_link">«</a></li>').appendTo(pager);
        }

        var curr = 0;
        while(numPages > curr && (settings.hidePageNumbers==false)){
            $('<li><a href="#" class="page_link">'+(curr+1)+'</a></li>').appendTo(pager);
            curr++;
        }

        if (settings.showPrevNext){
            $('<li><a href="#" class="next_link">»</a></li>').appendTo(pager);
        }

        pager.find('.page_link:first').addClass('active');
        pager.find('.prev_link').hide();
        if (numPages<=1) {
            pager.find('.next_link').hide();
        }
          pager.children().eq(1).addClass("active");

        children.hide();
        children.slice(0, perPage).show();

        pager.find('li .page_link').click(function(){
            var clickedPage = $(this).html().valueOf()-1;
            goTo(clickedPage,perPage);
            return false;
        });
        pager.find('li .prev_link').click(function(){
            previous();
            return false;
        });
        pager.find('li .next_link').click(function(){
            next();
            return false;
        });

        function previous(){
            var goToPage = parseInt(pager.data("curr")) - 1;
            goTo(goToPage);
        }

        function next(){
            var goToPage = parseInt(pager.data("curr")) + 1;
            goTo(goToPage);
        }

        function goTo(page){
            var startAt = page * perPage,
                endOn = startAt + perPage;

            children.css('display','none').slice(startAt, endOn).show();

            if (page>=1) {
                pager.find('.prev_link').show();
            }
            else {
                pager.find('.prev_link').hide();
            }

            if (page<(numPages-1)) {
                pager.find('.next_link').show();
            }
            else {
                pager.find('.next_link').hide();
            }

            pager.data("curr",page);
            pager.children().removeClass("active");
            pager.children().eq(page+1).addClass("active");

        }
        if (numPages<=1) {
            pager.hide();
        }
    };
      $('#recharge_history_table_body').pageMe({pagerSelector:'#recharge_history_page',showPrevNext:true,hidePageNumbers:false,perPage:3});
      $('#usage_history_table_body').pageMe({pagerSlector:'#usage_history_page',showPrevNext:true,hidePageNumbers:false,perPage:3});
});