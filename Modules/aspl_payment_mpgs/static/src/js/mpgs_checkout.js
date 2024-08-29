/** @odoo-module **/

import { _t } from '@web/core/l10n/translation';
import paymentForm from '@payment/js/payment_form';
import { RPCError } from '@web/core/network/rpc_service';

paymentForm.include({
    _initiatePaymentFlow(providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'mpgs') {
            this._super(...arguments); // Tokens are handled by the generic flow
            return;
        } else {
            flow = 'mpgs';
            var new_data = null;
            this.rpc(
                this.paymentContext['transactionRoute'],
                this._prepareTransactionRouteParams(),
            ).then(processingValues => {
                if (flow === 'redirect') {
                    this._processRedirectFlow(
                        providerCode, paymentOptionId, paymentMethodCode, processingValues
                    );
                } else if (flow === 'mpgs') {
                        this.rpc("/get_mpgs_data",       {}).then(function (data) {
                        var new_data = data;
                        Checkout.configure({
                            merchant: new_data.merchant_id,
                            order: {
                                amount: new_data.amount,
                                currency: new_data.currency,
                                description: new_data.order_name,
                                id: new_data.order_id,
                            },
                            billing: {
                                address: {
                                    street: new_data.cust_street,
                                    city: new_data.cust_city,
                                    postcodeZip: new_data.cust_zip,
                                    stateProvince: new_data.cust_state_code,
                                    country: new_data.cust_country,
                                }
                            },
                            customer: {
                                email: new_data.cust_email,
                                phone: new_data.cust_phone
                            },
                            interaction: {
                                merchant: {
                                    name: new_data.merchant_name,
                                    address: {
                                        line1: new_data.address1,
                                        line2: new_data.address2
                                    }
                                },
                            },
                            session: {
                                id: new_data.session_id,
                                version: new_data.session_version
                            },
                        });

                        setTimeout(function () {
                            Checkout.showLightbox();
                        }, 100);
                    });
                    this._processDirectFlow(
                        providerCode, paymentOptionId, paymentMethodCode, processingValues
                    );
                } else if (flow === 'direct') {
                    this._processDirectFlow(
                        providerCode, paymentOptionId, paymentMethodCode, processingValues
                    );
                } else if (flow === 'token') {
                    this._processTokenFlow(
                        providerCode, paymentOptionId, paymentMethodCode, processingValues
                    );
                }
            }).catch(error => {
                if (error instanceof RPCError) {
                    this._displayErrorDialog(_t("Payment processing failed"), error.data.message);
                    this._enableButton(); // The button has been disabled before initiating the flow.
                } else {
                    return Promise.reject(error);
                }
            });
        }
    },
});
