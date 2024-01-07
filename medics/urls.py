from django.urls import path, include
from .views import *

urlpatterns = [
    # Medics
    # path('medic/<int:pk>/', MedicGetOne.as_view()),
    # path('medics-transfer-data/', MedicTransferData.as_view()),
    path('medics-salary-payments-transfer-data/', MedicSalaryPaymentsTransferData.as_view()),

    path('medic/<int:pk>/', MedicGetOne.as_view()),
    path('medics/<int:pk>/delete/', MedicGetOne.as_view()),

    path('medics/', MedicListCreate.as_view()),
    path('medics/month/<str:month>/', MedicListByMonth.as_view()),
    path('medics/<str:pk>/', MedicGetUpdateDelete.as_view()),
    path('medics/<str:pk>/salary/<str:date>/', MedicGetSalary.as_view()),

    # Med Product
    path('medics/<int:pk>/products-bot/', MedGetProducts.as_view()),
    path('medics/products/<str:pk>/destroy/<str:p_id>/', MedProductDestroy.as_view()),
    # path('medics/<int:pk>/products/', MedGetProducts.as_view()),
    # path('medics/products/<int:pk>/destroy/<int:p_id>/', MedProductDestroy.as_view()),
    path('medics/products/', MedProductListCreate.as_view()),
    path('medic-product/', MedProductPost.as_view()),
    path('medics/products/<str:pk>/product/<str:p_id>/', MedProductGetUpdateDelete.as_view()),

    # Med Salary
    path('medics/salary/payments/', MedSalaryPaymentListCreate.as_view()),
    path('medics/salary/payments/<str:pk>/', MedSalaryPaymentGetUpdateDelete.as_view()),
    path('medics-salary/payments/<str:pk>/', MedSalaryPaymentGetPayments.as_view()),

    path('medics-main/month/<str:month>/', MedicMainPageAPI.as_view()),
    path('medics-profile/', MedicProfilePageAPI.as_view()),
    path('medics-products/', MedicProductsPageAPI.as_view()),
    path('medics-statistics/month/<str:month>/', MedicStatisticsPageAPI.as_view()),

]
