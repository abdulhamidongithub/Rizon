from django.urls import path, include
from .views import *

urlpatterns = [
    # Warehouse
    path('warehouses-sales-transfer-data/', WarehoueseTransferSaleData.as_view()),
    path('warehouses-products-transfer-data/', WarehouseProductTransferData.as_view()),

    path('warehouses/', WarehouseListCreate.as_view()),
    path('warehouses/products-sale-by-month-to-month/', WarehouseProductsSaleByMonthToMonth.as_view()),
    path('warehouses/products-send-by-month-to-month/', WarehouseProductsSendByMonthToMonth.as_view()),
    path('warehouses/<str:pk>/', WarehouseGetUpdateDelete.as_view()),

    path('mini-warehouses/', WarehouseList.as_view()),
    path('warehouses/<str:pk>/employees/', WarehouseGetEmployees.as_view()),
    path('warehouses/<str:pk>/products/sum/', WarehouseGetProducts.as_view()),

    # Warehouse Products
    path('warehouses/products/', WarehouseProductListCreate.as_view()),
    path('warehouses/products/<str:pk>/', WarehouseProductGetUpdateDelete.as_view()),

    # WarehouseSaleProduct
    path('warehouses/sale/products/', WarehouseSaleProductListCreate.as_view()),
    path('warehouses/sale/products/fr-bot/', WarehouseSaleProductListCreateForFRBot.as_view()),

    path('warehouses/sale/products/<str:pk>/', WarehouseSaleProductGetUpdateDelete.as_view()),
    path('warehouses/sale/products/<str:pk>/endswith/', WarehouseSaleProductGetEndsWith.as_view()),
    path('warehouses/sale/products/<str:date>/data/', WarehouseSaleProductsGetDataByMonth.as_view()),
]
