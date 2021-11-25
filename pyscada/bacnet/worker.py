#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import SingleDeviceDAQProcessWorker
from pyscada.models import Device


import json
import logging


logger = logging.getLogger(__name__)


class Process(SingleDeviceDAQProcessWorker):
    device_filter = dict(bacnetdevice__isnull=False, bacnetdevice__device_type=0)
    process_class = 'pyscada.bacnet.device.Process'
    bp_label = 'pyscada.bacnet-%s'

    def __init__(self, dt=5, **kwargs):
        super(SingleDeviceDAQProcessWorker, self).__init__(dt=dt, **kwargs)

    #def gen_group_id(self, item):
    #    return '%d-%s:%s' % (item.pk, item.bacnetdevice.ip_address, item.bacnetdevice.port)
