/** @odoo-module **/

import { _t } from '@web/core/l10n/translation';
// import paymentForm from '@payment/js/payment_form';
import { RPCError } from '@web/core/network/rpc_service';

// odoo.define('aspl_payment_hobex_ee.main', function (require) {
//     "use strict";
    // var ajax = require('web.ajax')
    var wpwlOptions = {
        style: "card",
        paymentTarget: "_top",
        forceCardHolderEqualsBillingName: true
    }

    function getCardConnectHandler() {
        $(document).find('#modalHobex').modal('show')
    }

    function display_hobex_form(provider_form) {
    var wpwlOptions = {
             locale: "en",
            style:"card",
            onReady:function(){
            $(".wpwl-brand-SOFORTUEBERWEISUNG").click(function(){$(".wpwl-form-onlineTransfer-SOFORTUEBERWEISUNG .wpwl-group-country, .wpwl-form-onlineTransfer-SOFORTUEBERWEISUNG .wpwl-wrapper-submit").slideToggle()});
            $(".wpwl-brand-GIROPAY").click(function(){$(".wpwl-form-onlineTransfer-GIROPAY .wpwl-group-accountBankBic, .wpwl-form-onlineTransfer-GIROPAY .wpwl-wrapper-submit").slideToggle()})
           }
        }

        var payment_form = $('.o_payment_form');
        if (!payment_form.find('i').length)
            payment_form.append('<i class="fa fa-spinner fa-spin"/>');
        payment_form.attr('disabled', 'disabled');

        var provider_id = $(document).find('input[name="provider"]:checked').val();
        var so_id = $(document).find('#so_id').val();
        if (!provider_id) {
            return false;
        }
          var create_tx = this.rpc('/shop/payment/transaction/' + provider_id, 'call', {
             so_id: so_id,
             provider_id: provider_id
         }, {async: false}).then(function (data) {
             try {
                 provider_form.innerHTML = data;
             } catch (e) {
             }
         });
         create_tx.done(function () {
            getCardConnectHandler()
         });
    }

    $(document).on('click','.hobex_paynow',function(){
        display_hobex_form($('form[provider="hobex"]'));
    });

// });
//.hobex_pay