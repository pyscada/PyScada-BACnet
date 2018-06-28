# -*- coding: utf-8 -*-
from __future__ import unicode_literals


__version__ = '0.7.0rc6'
__author__ = 'Martin Schröder'

default_app_config = 'pyscada.bacnet.apps.PyScadaBACnetConfig'

PROTOCOL_ID = 4

parent_process_list = [{'pk': PROTOCOL_ID,
                        'label': 'pyscada.bacnet',
                        'process_class': 'pyscada.bacnet.worker.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]