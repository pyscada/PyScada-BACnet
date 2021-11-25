# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from pyscada.bacnet.models import BACnetDevice, BACnetVariable, ExtendedBACnetDevice, ExtendedBACnetVariable

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BACnetDevice)
@receiver(post_save, sender=BACnetVariable)
@receiver(post_save, sender=ExtendedBACnetDevice)
@receiver(post_save, sender=ExtendedBACnetVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is BACnetDevice:
        post_save.send_robust(sender=Device, instance=instance.bacnet_device)
    elif type(instance) is BACnetVariable:
        post_save.send_robust(sender=Variable, instance=instance.bacnet_variable)
    elif type(instance) is ExtendedBACnetVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedBACnetDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))


@receiver(pre_delete, sender=BACnetDevice)
@receiver(pre_delete, sender=BACnetVariable)
@receiver(pre_delete, sender=ExtendedBACnetDevice)
@receiver(pre_delete, sender=ExtendedBACnetVariable)
def _del_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is BACnetDevice:
        pre_delete.send_robust(sender=Device, instance=instance.bacnet_device)
    elif type(instance) is BACnetVariable:
        pre_delete.send_robust(sender=Variable, instance=instance.bacnet_variable)
    elif type(instance) is ExtendedBACnetVariable:
        pre_delete.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedBACnetDevice:
        pre_delete.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))
