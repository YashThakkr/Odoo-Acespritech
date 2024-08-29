odoo.define('odoo_auto_logout', function(require) {
    "use strict";
    var rpc = require('web.rpc');
    var session = require('web.session');

    rpc.query({
        model: 'res.company',
        method: 'read',
        args: [[session.company_id],['logout_time']],
    }).then(function(result) {
        if (result) {
            window.timeout = setTimeout(function() {
                    window.location.href = "/web/session/logout?redirect=/"; 
                }, result[0]['logout_time'] *1000);
            $(document).on('mousemove', function() {
                if (window.timeout !== null) {
                    clearTimeout(window.timeout);
                }
                window.timeout = setTimeout(function() {
                    window.location.href = "/web/session/logout?redirect=/"; 
                }, result[0]['logout_time'] *1000);
            });
        }
    });
});
