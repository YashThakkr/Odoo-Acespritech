import json
import logging
import re

from lxml import etree
import odoo as odoo1
from odoo import api, models, _
import shutil
import os

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'
    

    def restrict_clear_session(self):
        path = odoo1.tools.config.session_dir
        shutil.rmtree(path)
        os.mkdir(path,mode = 0o777)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }