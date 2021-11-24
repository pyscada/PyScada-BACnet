# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaBACnetConfig(AppConfig):
    name = 'pyscada.bacnet'
    verbose_name = _("PyScada BACnet Master")
    path = os.path.dirname(os.path.realpath(__file__))

    def ready(self):
        import pyscada.modbus.signals