odoo.define('aspl_payment_bluepay.bluepay_checkout', require => {
    'use strict';

   $(document).ready(function(e) {
      var new_data = null
      var ajax = require('web.ajax');
      ajax.jsonRpc("/get_bluepay_data", 'call', {}, {
         'async' : false})
      // alert(">>>>>>>")
      
      // }).then(function(main_url) {
      //    window.open(main_url, '_self');
      // });
   });
});
