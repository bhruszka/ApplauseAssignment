from django.contrib import admin
from .models import Device, Tester, Bug


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    pass


@admin.register(Tester)
class TesterAdmin(admin.ModelAdmin):
    pass


@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    pass
