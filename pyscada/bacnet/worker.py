#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import MultiDeviceDAQProcessWorker
from pyscada.models import Device, BackgroundProcess
from pyscada.bacnet import PROTOCOL_ID


import json
import logging


logger = logging.getLogger(__name__)


class Process(MultiDeviceDAQProcessWorker):
    device_filter = dict(bacnetdevice__isnull=False, bacnetdevice__device_type=0, protocol_id=PROTOCOL_ID)
    process_class = 'pyscada.bacnet.device.Process'
    bp_label = 'pyscada.bacnet-%s'

    def __init__(self, dt=5, **kwargs):
        super(MultiDeviceDAQProcessWorker, self).__init__(dt=dt, **kwargs)

    def init_process(self):
        super(Process, self).init_process()
        for process in self.processes:
            bp = BackgroundProcess.objects.filter(pk=process['id'])
            device_ids = [Device.objects.get(id=process['device_ids'][0]).pk]
            for item in Device.objects.filter(active=True, bacnetdevice__isnull=False, bacnetdevice__bacnet_local_device=process['device_ids'][0]):
                device_ids.append(item.pk)
            bp.update(process_class_kwargs=json.dumps({'device_ids': [i for i in device_ids]}))
            process['device_ids'] = device_ids
            self.processes.remove(process)
            self.processes.append(process)

    def gen_group_id(self, item):
        return '%d-%s:%s' % (item.pk, item.bacnetdevice.ip_address, item.bacnetdevice.port)
