# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, DeviceProtocol
from pyscada.models import Variable
from . import PROTOCOL_ID

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.forms.models import BaseInlineFormSet

import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class BACnetDevice(models.Model):
    bacnet_device = models.OneToOneField(Device, null=True, blank=True, on_delete=models.CASCADE)
    device_type_choices = ((0, 'Local'), (1, 'Remote'),)
    device_type = models.PositiveSmallIntegerField(default=0, help_text='Set a local bacnet device to discover remote'
                                                                        ' BACNet devices on the network',
                                                   choices=device_type_choices)
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    mask = models.PositiveSmallIntegerField(default=24, help_text="Network mask for local device only")
    port = models.CharField(default='47808',
                            max_length=400,
                            help_text="for IP default port is 47808")
    bacnet_local_device = models.ForeignKey(Device, null=True, blank=True, on_delete=models.CASCADE,
                                            related_name='bacnet_remote_devices')

    def __str__(self):
        return self.bacnet_device.short_name

    fk_name = 'bacnet_device'

    class FormSet(BaseInlineFormSet):
        def add_fields(self, form, index):
            super().add_fields(form, index)
            if form.initial:
                form.fields['device_type'].disabled = True
                form.fields['bacnet_local_device'].queryset = Device.objects.filter(bacnetdevice__isnull=False,
                                                                                    bacnetdevice__device_type=0)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Meta:
        verbose_name = 'BACnet Device'
        verbose_name_plural = 'BACnet Devices'

    protocol_id = PROTOCOL_ID

    def parent_device(self):
        try:
            return self.bacnet_device
        except:
            return None


@python_2_unicode_compatible
class BACnetDeviceProperty(models.Model):
    bacnet_device = models.ForeignKey(BACnetDevice, on_delete=models.CASCADE)
    property_id = models.PositiveIntegerField()  # TODO add choices
    value = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'BACnet Device Property'
        verbose_name_plural = 'BACnet Device Properties'

    def name(self):
        return 'none'  # TODO get name from choices

    def __str__(self):
        return self.bacnet_device.short_name


@python_2_unicode_compatible
class BACnetVariable(models.Model):
    bacnet_variable = models.OneToOneField(Variable, null=True, blank=True, on_delete=models.CASCADE)
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
        return self.bacnet_variable.name

    class Meta:
        verbose_name = 'BACnet Variable'
        verbose_name_plural = 'BACnet Variables'

    protocol_id = PROTOCOL_ID


@python_2_unicode_compatible
class BACnetVariableProperty(models.Model):
    bacnet_variable = models.ForeignKey(BACnetVariable, on_delete=models.CASCADE)
    id_choices = ()
    try:
        from bacpypes.basetypes import PropertyIdentifier
        for key, val in PropertyIdentifier.enumerations.items():
            id_choices += ((val, key,),)
    except ImportError:
        pass
    property_id = models.PositiveIntegerField(choices=id_choices)  # TODO add choices
    priority = models.PositiveIntegerField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)

    def name(self):
        return 'none'  # TODO get name from choices

    def __str__(self):
        return self.bacnet_variable.bacnet_variable.name + "-" + self.id_choices[self.property_id][1]

    class Meta:
        verbose_name = 'BACnet Variable Property'
        verbose_name_plural = 'BACnet Variable Properties'


class ExtendedBACnetDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'BACnet Device'
        verbose_name_plural = 'BACnet Devices'


class ExtendedBACnetVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'BACnet Variable'
        verbose_name_plural = 'BACnet Variables'


@receiver(post_save, sender=BACnetDevice)
@receiver(post_save, sender=BACnetVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is BACnetDevice:
        post_save.send_robust(sender=Device, instance=instance.bacnet_device)
    elif type(instance) is BACnetVariable:
        post_save.send_robust(sender=Variable, instance=instance.bacnet_variable)
