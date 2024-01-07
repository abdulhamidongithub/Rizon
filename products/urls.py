from django.urls import path, include
from .views import *

urlpatterns = [
    # Medics
    path('products-transfer-data/', ProductsTransferData.as_view()),
    path('product-template/<uuid:pk>/', view_product_template),

    path('products/', ProductListCreate.as_view()),
    path('product/<str:name>/', ProductGetOne.as_view()),
    path('products/<str:pk>/', ProductGetUpdateDelete.as_view()),
    path('products-distribution/', ProductDistributionList.as_view()),
    path('products/discount/', ProductDiscountListCreate.as_view()),
    path('products/discount/create/', ProductDiscountCreate.as_view()),
    path('products/discount/<str:pk>/', ProductDiscountGetDestroy.as_view()),
    # path('products/<int:pk>/discount/', ProductDiscountAPI.as_view()),
    # path('products/<int:pk>/discount/del/', ProductDiscountDestroyAPI.as_view()),
]
