# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.bacnet import PROTOCOL_ID
from pyscada.bacnet.models import BACnetDevice, ExtendedBACnetDevice
from pyscada.bacnet.models import (
    BACnetVariable,
    BACnetVariableProperty,
    ExtendedBACnetVariable,
)
from pyscada.admin import DeviceAdmin
from pyscada.admin import VariableAdmin
from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol
from pyscada.models import Variable
from django.contrib import admin

import logging

logger = logging.getLogger(__name__)


class BACnetDeviceAdminInline(admin.StackedInline):
    model = BACnetDevice


class BACnetDeviceAdmin(DeviceAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "protocol":
            kwargs["queryset"] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(BACnetDeviceAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(BACnetDeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [BACnetDeviceAdminInline]


class BACnetVariableAdminInline(admin.StackedInline):
    model = BACnetVariable


class BACnetVariableAdmin(VariableAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "unit",
        "device_name",
        "value_class",
        "active",
        "writeable",
        "address",
        "function_code_read",
    )
    list_editable = (
        "active",
        "writeable",
    )
    list_display_links = ("name",)

    def address(self, instance):
        return instance.BACnetvariable.address

    def function_code_read(self, instance):
        return instance.bacnetvariable.function_code_read

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(BACnetVariableAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(BACnetVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [BACnetVariableAdminInline]


# admin_site.register(ExtendedBACnetDevice, BACnetDeviceAdmin)
# admin_site.register(ExtendedBACnetVariable, BACnetVariableAdmin)
admin_site.register(BACnetVariableProperty)
