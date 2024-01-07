from django.urls import path

from products.views import ProductOrderCreate, ProductOrderGetUpdateDestroy
from .views import *
from .views import CreateUserView, VerifyAPIView, GetNewVerification, \
    ChangeUserInformationView, ChangeUserPhotoView, LoginView, LoginRefreshView, \
    LogOutView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('login/refresh/', LoginRefreshView.as_view()),
    path('logout/', LogOutView.as_view()),
    path('signup/', CreateUserView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('new-verify/', GetNewVerification.as_view()),
    path('change-user-info/', ChangeUserInformationView.as_view()),
    path('change-user-photo/', ChangeUserPhotoView.as_view()),
    path('users-forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
    # path('users/update-username-password/', UsersUpdateUsernamePasswordAPIView.as_view()),
    path('user-auto-delete-users-last-month-frbot/', UsersAutoDeleteFRBotAPIView.as_view()),
    path('user-auto-delete-users-last-six-month-frbot/', UsersAutoDeleteLastSixMonthFRBotAPIView.as_view()),

    path('users/template/', UsersTemplateView.as_view()),
    path('user-get-coupons-frbot/', GetUsersCouponsSumFRBot.as_view()),
    path('user-tree-update-date-main-py/', UsersTreeUpdateDateAPIViewMainPy.as_view()),
    path('user-update-frbot/<int:user_id>/', UserUpdateAPIView.as_view()),
    path('user-create-frbot/', UsersCreateFRBotAPIView.as_view()),
    path('brand-manager-create-frbot/', BrandManagerCreateFRBotAPIView.as_view()),
    path('brand-manager-delete-frbot/<int:user_id>/', BrandManagerDeleteFRBotAPIView.as_view()),
    path('check-passport/<str:passport>/', CheckPasswordAPIView.as_view()),
    path('users/<str:pk>/all_bonuses/<str:date>/old/', UserGetAllInfoOldAPIView.as_view()),

    path('users-transfer-data/', UsersTransferData.as_view()),
    path('users-tree-transfer-data/', UsersTreeTransferData.as_view()),
    path('users-transfer-data-update-date/<int:user_id>/date/<str:date>/', UserUpdateJoinedDateView.as_view()),

    path('users-salary-payments-transfer-data/', UserSalaryPaymentsTransferView.as_view()),
    # path('users/<int:pk>/tree/template/', UserTreeView.as_view()),
    path('users/<str:pk>/salary/pay/month/<str:month>/', UserSalaryPayGet.as_view()),
    path('users/<str:pk>/last/sale/', UsersGetLastSale.as_view()),
    path('users/<str:pk>/tree/', UserTreeGet.as_view()),
    path('users/<str:pk>/tree/date/<str:month>/', UserTreeGetInfo.as_view()),
    path('users/<str:pk>/tree/first/', UserTreeGetFirstTree.as_view()),
    path('users/<int:pk>/user_id/', UserGetOne.as_view()),
    path('users/<int:pk>/user_id/with_teacher/', UserGetOneWithTeacher.as_view()),
    path('users/<str:pk>/sales/date/<str:startDate>/<str:endDate>/', UsersGetSalesByDate.as_view()),
    path('users/', UsersListCreate.as_view()),

    path('users-main/', UserMainPageAPI.as_view()),
    path('users-main-a/', UserMainPageAPIAndroid.as_view()),
    path('users-products/', UserProductPageAPI.as_view()),
    path('users-orders/', UserOrdersPageAPI.as_view()),
    path('users-coupons/', UserCouponsPageAPI.as_view()),
    path('users-notifications/', UserNotificationsAPI.as_view()),

    path('users-promotions/', UsersPromotionPageAPIView.as_view()),
    path('users-promotions/<str:pk>/', UsersPromotionGetAPIView.as_view()),
    path('users-promotions-purchases/', UsersPromotionPurchasesPageAPIView.as_view()),
    path('users-prms/history/', UsersPromotionPurchasesAPIView.as_view()),
    path('users-promotions/buy/', UsersPromotionBuyAPIView.as_view()),
    path('users-promotions-buy/', UsersPromotionBuyAPIView.as_view()),
    path('users-promotions/user_buy/', usersPromotionBuyAPIViewFunc),

    path('users-sales/', UserSalesAPI.as_view()),
    path('users-profile/month/<str:month>/', UserProfileAPI.as_view()),
    path('users-profil/month/<str:month>/', UserProfileAPIAndroid.as_view()),
    path('users-discounts/', UsersProductDiscountAPIView.as_view()),

    path('brand-manager-main/', UserMainPageAPI.as_view()),
    path('brand-manager-products/', UserProductPageAPI.as_view()),
    path('brand-manager-orders/', UserOrdersPageAPI.as_view()),
    path('brand-manager-coupons/', UserCouponsPageAPI.as_view()),
    path('brand-manager-notifications/', UserNotificationsAPI.as_view()),

    path('brand-manager-promotions/', UsersPromotionPageAPIView.as_view()),
    path('brand-manager-promotions/<str:pk>/', UsersPromotionGetAPIView.as_view()),
    path('brand-manager-promotions/purchases/', UsersPromotionPurchasesPageAPIView.as_view()),
    path('brand-manager-promotions/buy/', UsersPromotionBuyAPIView.as_view()),
    path('brand-manager-promotions/user_buy/', usersPromotionBuyAPIViewFunc),

    path('brand-manager-sales/', UserSalesAPI.as_view()),
    path('brand-manager-profile/month/<str:month>/', UserProfileAPI.as_view()),
    path('brand-manager-discounts/', UsersProductDiscountAPIView.as_view()),

    path('users/<str:pk>/', UsersGetUpdateDelete.as_view()),
    path('users/<str:pk>/all_bonuses/<str:date>/', UserGetAllInfo.as_view()),
    # path('users/<int:pk>/all_bonuses/<str:date>/22/', UserGetAllInfo2222222222.as_view()),

    # Users Tree
    # path('users/tree/', UsersTreeListCreate.as_view()),
    # path('users/tree/<int:pk>/', UsersTreeGetUpdateDelete.as_view()),

    # Users Order
    path("users/product/order/", ProductOrderCreate.as_view()),
    path("users/product/order/<str:pk>/", ProductOrderGetUpdateDestroy.as_view()),

    # Users Salary
    path('users/salary/payments/', UsersSalaryListCreate.as_view()),
    path('users/salary/payments/<str:pk>/', UsersSalaryGetUpdateDelete.as_view()),
    path('users-salary/payments/<str:pk>/', UsersSalaryGetPayments.as_view()),
    path('users/<str:pk>/salary/payments/', UserSalaryHistory.as_view()),
    path('users-salary/payments/', UserSalaryHistory2.as_view()),
    path('users-bonus-accounts/', UserBonusAccounts.as_view()),

    # Users Coupon
    # path('coupons/user/<int:user_id>/<int:coupon>/', UsersCouponCreate.as_view()),
    path('coupons/user/sum/<uuid:pk>/', UsersCouponUsedSum.as_view()),
    path('coupons/user-sum/', UsersCouponUsedSumForUser.as_view()),
    path('coupons/', UsersCouponListCreate.as_view()),
    path('coupons/transfers/', UsersCouponTransferCreateAPI.as_view()),
    path('coupons/transfers/<str:pk>/', UsersCouponTransferGetAPI.as_view()),
    path('coupons/<str:pk>/', UsersCouponGetUpdateDelete.as_view()),
    path('undelete-users/', UndeleteUsersApiView.as_view()),

    path('get-own-family-tree/<str:month>/', GetShajaraByFamilyTreeAPIView.as_view()),
    path('get-own-family-tree/<str:month>/<uuid:pk>/', GetShajaraByFamilyTreeSelfAPIView.as_view()),
]
