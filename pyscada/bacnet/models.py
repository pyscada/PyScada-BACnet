# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device
from pyscada.models import Variable

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class BACnetDevice(models.Model):
    bacnet_device = models.OneToOneField(Device, null=True, blank=True)
    vendor_name = models.CharField(max_length=200)
    vendor_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=200)
    product_model_number = models.CharField(max_length=200)
    product_description = models.CharField(max_length=400)
    device_id = models.PositiveIntegerField(unique=True)
    mac = models.CharField(max_length=14)  # xx:xx:xx:xx:xx

    def __str__(self):
        return self.bacnet_device.short_name


@python_2_unicode_compatible
class BACnetDeviceProperty(models.Model):
    bacnet_device = models.ForeignKey(BACnetDevice)
    property_id = models.PositiveIntegerField()  # TODO add choises
    value = models.CharField(max_length=200)

    def name(self):
        return 'none'  # TODO get name from choices

    def __str__(self):
        return self.bacnet_device.short_name


@python_2_unicode_compatible
class BACnetObject(models.Model):
    bacnet_variable = models.OneToOneField(Variable, null=True, blank=True)
    bacnet_device = models.ForeignKey(BACnetDevice)
    object_identifier = models.PositiveIntegerField()
    object_type_choises = ()
    try:
        from bacpypes.basetypes import ObjectTypesSupported
        for key, val in ObjectTypesSupported.bitNames.items():
            object_type_choises += ((val, key,),)
    except ImportError:
        pass
    object_type = models.PositiveIntegerField(choices=object_type_choises)

    def __str__(self):
        return self.bacnet_device.short_name


@python_2_unicode_compatible
class BACnetObjectProperty(models.Model):
    bacnet_device = models.ForeignKey(BACnetObject)
    id_choises = ()
    try:
        from bacpypes.basetypes import PropertyIdentifier
        for key, val in PropertyIdentifier.enumerations.items():
            id_choises += ((val, key,),)
    except ImportError:
        pass
    property_id = models.PositiveIntegerField(choices=id_choises)  # TODO add choises
    priority = models.PositiveIntegerField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)

    def name(self):
        return 'none'  # TODO get name from choices

    def __str__(self):
        return self.bacnet_device.short_name


@receiver(post_save, sender=BACnetDevice)
@receiver(post_save, sender=BACnetObject)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is BACnetDevice:
        post_save.send_robust(sender=Device, instance=instance.bacnet_device)
    elif type(instance) is BACnetObject:
        post_save.send_robust(sender=Variable, instance=instance.bacnet_variable)
