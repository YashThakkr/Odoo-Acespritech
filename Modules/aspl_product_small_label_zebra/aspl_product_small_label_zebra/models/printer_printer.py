# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################


import logging
import os
import tempfile
import cups
_logger = logging.getLogger(__name__)
try:
    from tempfile import mkstemp
except ImportError:
    _logger.debug('Cannot `import tempfile`.')
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import subprocess


class printer_printer(models.Model):
    _name = 'printer.printer'
    _description = 'Printer'
    _order = 'name'

    name = fields.Char(required=True, index=True)
    server_id = fields.Many2one('printer.server', string='Server', required=True,
                                help='Server used to access this printer.')
    job_ids = fields.One2many('printer.job', 'printer_id', string='Jobs', help='Jobs printed on this printer.')
    system_name = fields.Char(required=True, index=True)
    default = fields.Boolean(readonly=True)
    status = fields.Selection([
        ('unavailable', 'Unavailable'),
        ('printing', 'Printing'),
        ('unknown', 'Unknown'),
        ('available', 'Available'),
        ('error', 'Error'),
        ('server-error', 'Server Error')],
        required=True, readonly=True, default='unknown')
    status_message = fields.Char(readonly=True)
    model = fields.Char(readonly=True)
    location = fields.Char(readonly=True)
    uri = fields.Char(string='URI', readonly=True)

    def _prepare_update_from_cups(self, cups_connection, cups_printer):
        mapping = {3: 'available', 4: 'printing', 5: 'error'}
        vals = {
            'name': cups_printer['printer-info'],
            'model': cups_printer.get('printer-make-and-model', False),
            'location': cups_printer.get('printer-location', False),
            'uri': cups_printer.get('device-uri', False),
            'status': mapping.get(cups_printer.get(
                'printer-state'), 'unknown'),
            'status_message': cups_printer.get('printer-state-message', ''),
        }
        return vals

    def print_options(self, report=None, format=None, copies=1):
        """ Hook to set print options """
        options = {}
        if format == 'raw':
            options['raw'] = 'True'
        if copies > 1:
            options['copies'] = str(copies)
        return options

    def print_document(self, report, content, format, copies=1):
        """ Print a file Format could be pdf, qweb-pdf, raw"""
        self.ensure_one()
        fd, file_name = tempfile.mkstemp()
        print("\n\n fd, file_name", fd, file_name)
        print("\n\n content[0]", content)
        try:
            with os.fdopen(fd, 'wb') as file:
                file.write(content[0])
            # os.write(fd, content[0])
            # os.write(fd, str.encode(str(content), 'utf-8'))
                os.close(fd)
        except Exception as e:
            print(f"Error writing content to file: {e}")

        # finally:
        return self.print_file(
            file_name, report=report, copies=copies, format=format)

    def print_file(self, file_name, report=None, copies=1, format=None):
        """ Print a file """
        self.ensure_one()

        connection = self.server_id._open_connection(raise_on_error=True)
        print("\n\n\n connection-------", connection)
        options = self.print_options(
            report=report, format=format, copies=copies)

        _logger.debug(
            'Sending job to CUPS printer %s on %s'
            % (self.system_name, self.server_id.address))
        try:
            connection.printFile(self.system_name,file_name,file_name,
                                 options=options)
        except cups.IPPError:
            cmd = [
                'lp',
                '-h', '%s:%s' % (self.server_id.address, self.server_id.port),
                '-d', self.system_name,
                ]

        for opt, val in options.items():
            cmd.append('-o')

            if val:
                cmd.append('%s=%s' % (opt, val))
            else:
                cmd.append(opt)
                cmd.append(file_name)
                subprocess.check_call(cmd)
        _logger.info("Printing job: '%s' on %s" % (
            file_name,
            self.server_id.address,
        ))
        return True

    def set_default_printer(self):
        if not self:
            return
        self.ensure_one()
        default_printers = self.search([('default', '=', True)])
        if default_printers:
            raise UserError(_('Only one printer can make as default printer.'))
        self.write({'default': True})
        return True

    def get_default(self):
        return self.search([('default', '=', True)], limit=1)

    def action_cancel_all_jobs(self):
        self.ensure_one()
        return self.cancel_all_jobs()

    def cancel_all_jobs(self, purge_jobs=False):
        for printer in self:
            connection = printer.server_id._open_connection()
            connection.cancelAllJobs(
                name=printer.system_name, purge_jobs=purge_jobs)

        # Update jobs' states into Odoo
        self.mapped('server_id').update_jobs(which='completed')
        return True

    def printer_enable(self):
        for printer in self:
            connection = printer.server_id._open_connection()
            connection.enablePrinter(printer.system_name)
        # Update printers' stats into Odoo
        self.mapped('server_id').update_printers()
        return True

    def printer_disable(self):
        for printer in self:
            connection = printer.server_id._open_connection()
            connection.disablePrinter(printer.system_name)
        # Update printers' stats into Odoo
        self.mapped('server_id').update_printers()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
