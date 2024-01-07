from django.urls import path
from others.views import AdminMainPageAPIView, WarehousesPageAPIView, WarehouseGetAllInfo, ProductPageAPIView, \
    StatisticPageAPIView, UsersPageAPIView, UserTreeGetInfo, UserSalesInfo, LandingProductsAPI, LandingHomeAPI, \
    LandingProductAPI, LandingAboutAPI, ProductDiscountAPIView, AdminPromotionPageAPIView, \
    AdminPromotionGetUpdateDestroyAPIView, PromotionAmountCreateAPIView, UsersSalaryCalculateAPIView, \
    AdminPromotionPauseAPIView, AdminNotificationsAPIView, AdminArchivePageApi, AdminFinancePageApi, \
    AdminArchiveWarehousePageAPI, AdminArchiveEmployeePageAPI, AdminArchiveProductPageAPI, \
    AdminArchiveUserActivatePageAPI, AdminArchiveUserInfoPageAPI, WarehousesPageInfoAPIView, \
    WarehousesPageDeleteAPIView, MiniWarehousesPageAPIView, MiniWarehouseGetAllInfo, AdminChangeUsersRoles, \
    AdminChangeUserRole, MiniWarehousesPageInfoAPIView, ManagersPageAPIView, EmployeeSalaryPaymentsAPI, \
    WarehouseSalesAPIView, SaleDeleteAPIView, GetEffectiveStartUsersByMonthApiView, GetUserBonusAccountDataAPIView, \
    TransferBonusAccountAPIView, UseBonusAccountAPIView, AdminUsersBonusAccountsDataAPIView, AdminParametrsAPIView, \
    UserNewMPBonusTestAPIView, get_user_tree_view, GetLastUsersAPIView, AdminMainPageAPIView2, WarehousesPageAPIViewV2, \
    WarehouseGetAllInfoV2, AdminStatisticsPageAPIViewV2, AdminProductDiscountDestroy, AdminUsersFilterAPIViewV2
from products.views import LandingProductOrderCreate


urlpatterns = [
    path("admin-main/month/<str:month>/", AdminMainPageAPIView.as_view()),
    path('users-effective-start/month/<str:month>/', GetEffectiveStartUsersByMonthApiView.as_view()),

    path("admin-warehouses/month/<str:month>/", WarehousesPageAPIView.as_view()),
    path("admin-warehouses/", WarehousesPageInfoAPIView.as_view()),
    path("admin-warehouses/<str:pk>/sales/", WarehouseSalesAPIView.as_view()),
    path("manager-warehouses/<str:pk>/sales/", WarehouseSalesAPIView.as_view()),
    path("admin-sales/<str:pk>/", SaleDeleteAPIView.as_view()),
    path("manager-sales/<str:pk>/", SaleDeleteAPIView.as_view()),
    path("admin-warehouses/<str:pk>/", WarehousesPageDeleteAPIView.as_view()),
    path('admin-warehouses/month/<str:month>/warehouse/<str:pk>/', WarehouseGetAllInfo.as_view()),

    path("admin-mini-warehouses/month/<str:month>/", MiniWarehousesPageAPIView.as_view()),
    path('admin-mini-warehouses/month/<str:month>/warehouse/<str:pk>/', MiniWarehouseGetAllInfo.as_view()),
    path("admin-mini-warehouses/", MiniWarehousesPageInfoAPIView.as_view()),

    path('admin-managers/month/<str:month>/', ManagersPageAPIView.as_view()),

    path('admin-employees/<str:pk>/payments/', EmployeeSalaryPaymentsAPI.as_view()),
    path('manager-employees/<str:pk>/payments/', EmployeeSalaryPaymentsAPI.as_view()),
    path('admin-products/', ProductPageAPIView.as_view()),
    path('admin-promotions/', AdminPromotionPageAPIView.as_view()),
    path('admin-promotions/<str:pk>/', AdminPromotionGetUpdateDestroyAPIView.as_view()),
    path('admin-promotions/amount/', PromotionAmountCreateAPIView.as_view()),
    path('admin-promotions/<str:pk>/pause/', AdminPromotionPauseAPIView.as_view()),

    path('admin-change-user-role/<str:pk>/', AdminChangeUsersRoles.as_view()),
    path('admin-change-user-tree/', AdminChangeUserRole.as_view()),

    path('admin-discounts/', ProductDiscountAPIView.as_view()),
    path('admin-notifications/', AdminNotificationsAPIView.as_view()),

    path('admin-statistics/month/<str:month>/', StatisticPageAPIView.as_view()),

    path('admin-users/month/<str:month>/', UsersPageAPIView.as_view()),
    path('admin-users/<str:pk>/month/<str:month>/', UserTreeGetInfo.as_view()),
    path('admin-users/<str:pk>/sales/', UserSalesInfo.as_view()),

    path('admin-finance/month/<str:month>/', AdminFinancePageApi.as_view()),
    path('admin-archive/', AdminArchivePageApi.as_view()),

    path('admin-archive/warehouse/<str:pk>/', AdminArchiveWarehousePageAPI.as_view()),
    path('admin-archive/employee/<str:pk>/', AdminArchiveEmployeePageAPI.as_view()),
    path('admin-archive/product/<str:pk>/', AdminArchiveProductPageAPI.as_view()),
    path('admin-archive/user/<str:pk>/', AdminArchiveUserActivatePageAPI.as_view()),
    path('admin-archive/user/<str:pk>/month/<str:month>/', AdminArchiveUserInfoPageAPI.as_view()),

    path('admin-users/salary/calculate/month/<str:month>/', UsersSalaryCalculateAPIView.as_view()),


    path('admin-get-user-bonus-account-data/<int:user_id>/', GetUserBonusAccountDataAPIView.as_view()),
    path('admin-transfer-user-bonus-account-data/', TransferBonusAccountAPIView.as_view()),
    path('admin-use-user-bonus-account-data/', UseBonusAccountAPIView.as_view()),
    path('admin-user-bonus-accounts-data/', AdminUsersBonusAccountsDataAPIView.as_view()),
    path('admin-parametrs/', AdminParametrsAPIView.as_view()),

                                        ###
    path('manager-user-bonus-accounts-data/', AdminUsersBonusAccountsDataAPIView.as_view()),
    path('manager-get-user-bonus-account-data/<int:user_id>/', GetUserBonusAccountDataAPIView.as_view()),
    path('manager-transfer-user-bonus-account-data/', TransferBonusAccountAPIView.as_view()),
    path('manager-use-user-bonus-account-data/', UseBonusAccountAPIView.as_view()),
    # Manager
    path("manager-main/month/<str:month>/", AdminMainPageAPIView.as_view()),

    path("manager-warehouses/month/<str:month>/", WarehousesPageAPIView.as_view()),
    path("manager-warehouses/", WarehousesPageInfoAPIView.as_view()),
    path("manager-warehouses/<str:pk>/", WarehousesPageDeleteAPIView.as_view()),
    path('manager-warehouses/month/<str:month>/warehouse/<str:pk>/', WarehouseGetAllInfo.as_view()),

    path("manager-mini-warehouses/month/<str:month>/", MiniWarehousesPageAPIView.as_view()),
    path('manager-mini-warehouses/month/<str:month>/warehouse/<str:pk>/', MiniWarehouseGetAllInfo.as_view()),
    path("manager-mini-warehouses/", MiniWarehousesPageInfoAPIView.as_view()),

    path('manager-managers/month/<str:month>/', ManagersPageAPIView.as_view()),

    path('manager-products/', ProductPageAPIView.as_view()),
    path('manager-promotions/', AdminPromotionPageAPIView.as_view()),
    path('manager-promotions/<str:pk>/', AdminPromotionGetUpdateDestroyAPIView.as_view()),
    path('manager-promotions/amount/', PromotionAmountCreateAPIView.as_view()),
    path('manager-promotions/<str:pk>/pause/', AdminPromotionPauseAPIView.as_view()),
    #
    # path('admin-change-user-role/', AdminChangeUsersRoles.as_view()),
    # path('admin-change-user-tree/', AdminChangeUserRole.as_view()),

    path('manager-discounts/', ProductDiscountAPIView.as_view()),
    path('manager-notifications/', AdminNotificationsAPIView.as_view()),

    path('manager-statistics/month/<str:month>/', StatisticPageAPIView.as_view()),

    path('manager-users/month/<str:month>/', UsersPageAPIView.as_view()),
    path('manager-users/<str:pk>/month/<str:month>/', UserTreeGetInfo.as_view()),
    path('manager-users/<str:pk>/sales/', UserSalesInfo.as_view()),

    path('manager-finance/month/<str:month>/', AdminFinancePageApi.as_view()),
    path('manager-archive/', AdminArchivePageApi.as_view()),

    path('manager-archive/warehouse/<str:pk>/', AdminArchiveWarehousePageAPI.as_view()),
    path('manager-archive/employee/<str:pk>/', AdminArchiveEmployeePageAPI.as_view()),
    path('manager-archive/product/<str:pk>/', AdminArchiveProductPageAPI.as_view()),
    path('manager-archive/user/<str:pk>/', AdminArchiveUserActivatePageAPI.as_view()),
    path('manager-archive/user/<str:pk>/month/<str:month>/', AdminArchiveUserInfoPageAPI.as_view()),


    path('landing-main/', LandingHomeAPI.as_view()),
    path('landing-products/', LandingProductsAPI.as_view()),
    path('landing-products/order/', LandingProductOrderCreate.as_view()),
    path('landing-products/<str:pk>/', LandingProductAPI.as_view()),
    path('landing-about/', LandingAboutAPI.as_view()),

    path('new-mp-test/<int:user_id>/month/<str:month>/', UserNewMPBonusTestAPIView.as_view()),
    path('users-ordered-by-date/', GetLastUsersAPIView.as_view()),
    path('user-tree-view/<int:user_id>/month/<str:month>/', get_user_tree_view),

    ##########################################################################################################

    path("v2/admin-main/month/<str:month>/", AdminMainPageAPIView2.as_view()),
    path("v2/manager-main/month/<str:month>/", AdminMainPageAPIView2.as_view()),

    path("v2/admin-warehouses/month/<str:month>/", WarehousesPageAPIViewV2.as_view()),
    path("v2/manager-warehouses/month/<str:month>/", WarehousesPageAPIViewV2.as_view()),

    path('v2/manager-warehouses/month/<str:month>/warehouse/<str:pk>/', WarehouseGetAllInfoV2.as_view()),
    path('v2/manager-warehouses/month/<str:month>/warehouse/<str:pk>/', WarehouseGetAllInfoV2.as_view()),

    path('v2/admin-statistics/month/<str:month>/', AdminStatisticsPageAPIViewV2.as_view()),
    path('v2/manager-statistics/month/<str:month>/', AdminStatisticsPageAPIViewV2.as_view()),

    path('v2/discounts-destroy/<uuid:pk>/', AdminProductDiscountDestroy.as_view()),
    path('v2/admin-users-filter/', AdminUsersFilterAPIViewV2.as_view()),
]
