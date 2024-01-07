from django.contrib import admin
from .models import User, UserConfirmation, UserSalary, UsersSalaryPayment, UsersTree, UserNotification, UsersCoupon, \
    CouponTransfer, Notification, OurTeam, BonusAccount


class UserModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'username', 'user_id', 'phone_number', "user_roles"]
    ordering = ['-date']
    search_fields = ['first_name', 'last_name', "username", "id", "user_roles", "user_id"]
    list_filter = ['deleted']  # filtering


class UserTreeModelAdmin(admin.ModelAdmin):
    list_display = ['invited', 'offerer', 'date', 'deleted']
    ordering = ['-date']
    search_fields = ['date', 'deleted', "invited__user_id"]


class UserNotificationModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'message', 'date']
    ordering = ['date']
    search_fields = ['title', 'message', 'date']


class NotificationModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'message', 'date']
    ordering = ['date']
    search_fields = ['title', 'message', 'date']


class UsersCouponModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'used', 'comment', 'dateTime']
    ordering = ['dateTime']
    search_fields = ['used', 'comment', 'dateTime']


class CouponTransferModelAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'used', 'comment', 'dateTime']
    ordering = ['dateTime']
    search_fields = ['used', 'comment', 'dateTime']


class UsersSalaryPaymentModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'paid', 'date', 'paymentDate', 'salary_payer']
    ordering = ['-paymentDate']
    search_fields = ['date', 'paymentDate', 'salary_payer']


class UserSalaryModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_status', 'user_score', 'user_tree_score',
                    'personal_bonus', 'coupon', 'salary', 'paid', 'debt', 'month']
    ordering = ['-month']
    search_fields = ['user_status', 'month', 'salary', 'paid', 'debt', 'user__user_id']


class BonusAccountModelAdmin(admin.ModelAdmin):
    list_display = ['bonus_type', 'user', 'status', 'amount', 'month']
    ordering = ['-created_time', ]
    search_fields = ['bonus_type', 'user__first_name', 'user__user_id', 'status', 'month']
    list_filter = ['bonus_type', 'month']


admin.site.register(User, UserModelAdmin)
admin.site.register(UserConfirmation)
admin.site.register(OurTeam)

admin.site.register(UserSalary, UserSalaryModelAdmin)
admin.site.register(BonusAccount, BonusAccountModelAdmin)
admin.site.register(UsersSalaryPayment, UsersSalaryPaymentModelAdmin)
admin.site.register(UsersTree, UserTreeModelAdmin)
admin.site.register(UserNotification, UserNotificationModelAdmin)
admin.site.register(UsersCoupon, UsersCouponModelAdmin)
admin.site.register(CouponTransfer, CouponTransferModelAdmin)
admin.site.register(Notification, NotificationModelAdmin)
