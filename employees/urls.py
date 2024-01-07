from django.urls import path, include

from .views import *


urlpatterns = [
    # Employee
    path('employee/<int:pk>/', EmployeeGetOne.as_view()),
    # path('employees-transfer-data/', EmployeeTransferData.as_view()),
    path('employees-create-frbot/', EmployeeCreateFRBotAPIView.as_view()),
    path('employees-salary-payments-transfer-data/', EmployeeSalaryPaymentsTransferAPIView.as_view()),

    # path('employee/<int:pk>/', EmployeeGetOne.as_view()),
    path('employees-transfer-data/', EmployeeTransferData.as_view()),

    path('employees-discounts/', EmployeeProductDiscountAPIView.as_view()),

    path('employees/', EmployeeListCreate.as_view()),
    path('employees/<str:pk>/', EmployeeGetUpdateDelete.as_view()),
    path('employees/<str:pk>/salary/<str:date>/', EmployeeGetSalary.as_view()),
    path('employees/<str:pk>/salary/<str:date>/fr-bot/', EmployeeGetSalaryFRBot.as_view()),

    # Employee Salary
    path('employees/salary/payments/', EmployeeSalaryPaymentListCreate.as_view()),
    path('employees/salary/payments/<str:pk>/', EmployeeSalaryPaymentGetDelete.as_view()),
    path('employees-salary/payments/<str:pk>/', EmployeeSalaryPaymentGetPayments.as_view()),
    path('employees-salary/payments/', OwnEmployeeSalaryPaymentGetPayments.as_view()),
    path("employees-sales/month/<str:month>/", EmployeeSalesMonthAPI.as_view()),

    path("employees-main/", EmployeeMainPageAPI.as_view()),

    path("employees-warehouse/", EmployeeWarehousePage.as_view()),
    path("employees-orders/", EmployeeOrdersPage.as_view()),

    path("employees-statistics/month/<str:month>/", EmployeeStatisticsPage.as_view()),

    path('employees-users/month/<str:month>/', EmployeeUsersPage.as_view()),
    path('employees-users/<str:pk>/sales/', EmployeeUsersGetSales.as_view()),
    path('employees-users/<str:pk>/month/<str:month>/', EmployeeUserTreeGetInfo.as_view()),

    path("employees-products/", EmployeeProductPage.as_view()),
    path("employees-products/<str:pk>/", EmployeeProductGet.as_view()),

    path("employees-profile/", EmployeeProfilePage.as_view()),

    path("employees-sale/mini-warehouses/", EmployeeSaleMiniWarehouse.as_view()),

    path("employees-get-user-bonus-account-data/<int:user_id>/", EmployeeGetUserBonusAccountDataAPIView.as_view()),
    path("employees-use-user-bonus-account-data/", EmployeeUseBonusAccountAPIView.as_view()),
    path("employees-users-bonus-account-data/", EmployeeUsersBonusAccountsDataAPIView.as_view()),

    path('employees-get-user-bonus-account-data/<int:user_id>/', EmployeeGetUserCashackForSaleAPIView.as_view()),
    path('employees-sale-products-fr-user-bonus/', EmployeeWarehouseSaleProductFromUserBonusesAPIView.as_view()),
]
