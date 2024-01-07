from django.contrib import admin
from .models import *


class WarehouseSaleProductModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'employee', 'warehouse', 'amount', 'summa', 'dateTime']
    ordering = ['-dateTime']
    search_fields = ['dateTime', 'amount', 'summa', 'user__user_id']

class WarehouseProductModelAdmin(admin.ModelAdmin):
    list_display = ['warehouse', 'product', 'amount', 'summa', 'paid', 'dateTime']
    ordering = ['-dateTime']
    search_fields = ['dateTime', 'amount', 'summa', 'paid', 'user__username', 'user__user_id']

class WarehouseModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'warehouse_type']
    # search_fields = []


admin.site.register(Warehouse, WarehouseModelAdmin)
admin.site.register(WarehouseProduct, WarehouseProductModelAdmin)
admin.site.register(WarehouseSaleProduct, WarehouseSaleProductModelAdmin)
