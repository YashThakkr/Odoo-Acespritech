/** @odoo-module */

import publicWidget from 'web.public.widget';
import rpc from 'web.rpc';
import ajax from 'web.ajax';
import core from 'web.core';

const QWeb = core.qweb;
const _t = core._t;

    publicWidget.registry.appointmentPage = publicWidget.Widget.extend({
        selector: ".oe_login_form, .form-group, #email_cus",
        events: {
            "change .radio": "_changeLoginType",
            "click #scan_rfid": "_clickScanRfid",
            "click .close": "_clickCloseButton",
            "keyup #login_email": "_onLoginEmailKeyUp"
        },

        init() {
            this._super.apply(this, arguments);
            if ($('input:radio[name="login_type"]:checked').val() == 'with_rfid') {
                $('#scan_rfid').show()
                $('#password_cus').hide()
                $('#login_btn').hide()
                $('#login_email_cust').hide()
                $("#login_email").prop('required', true);
                $("#login").prop('required', false);
                $("#password").prop('required', false);
                document.getElementById("login_btn").type = "button";

            }
            if ($('input:radio[name="login_type"]:checked').val() == 'without_rfid') {
                $('#scan_rfid').hide()
                $('#password_cus').show()
                $('#login_btn').show()
                $('#login_email_cust').show()
                $('#email_cus').hide()
                $("#login").prop('required', true);
                $("#password").prop('required', true);
                $("#login_email").prop('required', false);
                document.getElementById("login_btn").type = "submit";
            }
        },

        start: function () {
            var def = this._super.apply(this, arguments);
        },

        _onLoginEmailKeyUp: function(event) {
            if (event.keyCode === 13) {
                $(document).find('#scan_rfid').click();
                event.preventDefault();
            }
        },

        _changeLoginType: function () {
            if ($('input:radio[name="login_type"]:checked').val() == 'with_rfid') {
                $('#scan_rfid').show()
				$('#password_cus').hide()
				$('#login_btn').hide()
				$('#login_email_cust').hide()
				$("#login_email").prop('required', true);
				$("#login").prop('required', false);
				$("#password").prop('required', false);
				document.getElementById("login_btn").type = "button";
            }
            if ($('input:radio[name="login_type"]:checked').val() == 'without_rfid') {
                $('#scan_rfid').hide()
				$('#password_cus').show()
				$('#login_btn').show()
				$('#login_email_cust').show()
				$('#email_cus').hide()
				$("#login").prop('required', true);
				$("#password").prop('required', true);
				$("#login_email").prop('required', false);
				document.getElementById("login_btn").type = "submit";
            }
        },

        _clickScanRfid: function (e) {
            e.preventDefault();
            e.stopPropagation();
            ajax.jsonRpc("/check_email_user", 'call', {
				'email': $(document).find('#login_email').val()
			}).then(function(res) {
				if (res) {
					if (typeof $(document).find('#login_rfid_popup').html() !== 'undefined') {
						$(document).find('#login_rfid_popup').modal('show');
						$.rfidscan({
							parser: function (rawData) {
								if (rawData.length != 11) return null;
								else return rawData;
							},
							success: function (cardData) {
								ajax.jsonRpc("/check_user", 'call', {
									'card_no' : cardData.substr(0,10),
								}).then(function(res) {
									$("#login_rfid_popup").modal('hide');
									if (res && res.msg) {
										$.post("", {
											'msg': res.msg,
											'csrf_token': odoo.csrf_token,
											'user_id': res.user_id ? res.user_id : 0
										},function(res) {}).done(function() {
											if (res) {
												if (res.msg == 'success') {
													window.location.href = '/web'
												}
												if (res.msg == 'not_match') {
													$('#login_rfid_popup').modal('hide');
													setTimeout(function() {
														alert(_t('Not Match !! Please Try Again !!'));
														window.location.href = '/web/login'
													}, 1000);
												}
											}
										}).fail(function() {
											if (res) {
												window.location.href = '/web/login'
											}
										})
									}
								});
							},
						});
					}
				}
			});
        },

        _clickCloseButton: function () {
            $("#login_rfid_popup").modal('hide');
       }
});
