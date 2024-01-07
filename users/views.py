from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max
from django.shortcuts import render
# from django.utils.datetime_safe import datetime
from django.views import View
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import CreateAPIView, UpdateAPIView, get_object_or_404, RetrieveAPIView, ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from employees.employee_per import IsEmployee
from employees.models import Employee
from others.models import SalePromotion, Promotion, PromotionAmount
from others.rv_ball import rv_ball
from others.serializers import PromotionSerializer, SalePromotionSerializer, PostSalePromotionSerializer
from products.models import Product, ProductOrder, ProductDiscount
from products.serializers import ProductSerializer, ProductOrderSerializer, \
    forLandiingPoductSerializer, ProductDiscountSerializer
from shared.utility import send_email, check_email_or_phone, send_phone_code
from warehouses.models import WarehouseSaleProduct, Warehouse
from warehouses.serializers import WarehouseSaleProductSerializer
from .calculations import get_all_shajara, UserSalarySerializer, user_all_bonuses_test, user_all_bonuses2, get_user_tree, get_shajara_by_family_tree
from .serializers import SignUpSerializer, ChangeUserInformation, ChangeUserPhotoSerializer, LoginSerializer, \
    LoginRefreshSerializer, LogoutSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, \
    ForOthersUsersSerializer, UsersSerializer, UsersTreeSerializer, UsersSalarySerializer, \
    PostUsersSalarySerializer2, UsersCouponSerializer, PostUsersCouponSerializer, \
    PostCouponTransferSerializer, CouponTransferSerializer, UserNotificationSerializers, ForAdminUsersSerializer, BonusAccountSerializer
from .models import User
from uuid import uuid4


def get_the_month_specified_with_today_s_time(month: int):
    from datetime import date
    from datetime import datetime
    from dateutil import relativedelta

    date_time = str(datetime.today())
    m = date(year=int(date_time[:4]), month=int(date_time[5:7]), day=int(date_time[8:10]))
    selected_month = str(m - relativedelta.relativedelta(months=int(month)))
    return selected_month + date_time[10:]
    # return selected_month


class UsersAutoDeleteFRBotAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def delete(self, request, *args, **kwargs):
        data = []
        month = get_the_month_specified_with_today_s_time(1)
        users = User.objects.filter(date__startswith=month[:10], user_roles=ORDINARY_USER, deleted=False, auth_status=DONE)

        for user in users:
            sales = WarehouseSaleProduct.objects.filter(user=user)
            if sales:
                continue
            else:
                user_ser = UsersSerializer(user).data
                user_ser['sales'] = False
                del_phone = str(uuid4()).split("-")[-1]
                while User.objects.filter(phone_number=del_phone):
                    del_phone = f"{str(uuid4()).split('-')[-1]}"
                user.phone_number = del_phone
                user.deleted = True
                user.save()
                data.append(user_ser)

        return Response(
            {
                "success": True,
                "message": "Users has been deleted.",
                "users": data
            }
        )


class UsersAutoDeleteLastSixMonthFRBotAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def delete(self, request, *args, **kwargs):
        data = []
        month = get_the_month_specified_with_today_s_time(6)
        users = User.objects.filter(date__startswith=month[:10], user_roles=ORDINARY_USER, deleted=False, auth_status=DONE)

        for user in users:
            sales = WarehouseSaleProduct.objects.filter(user=user, dateTime__gte=month)
            if sales:
                continue
            else:
                user_ser = UsersSerializer(user).data
                user_ser['sales'] = False
                del_phone = str(uuid4()).split("-")[-1]
                while User.objects.filter(phone_number=del_phone):
                    del_phone = f"{str(uuid4()).split('-')[-1]}"
                user.phone_number = del_phone
                user.deleted = True
                user.save()
                data.append(user_ser)

        return Response(
            {
                "success": True,
                "message": "Users has been deleted.",
                "users": data
            }
        )


class UserTreeGet(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        tree = get_user_tree(kwargs['pk'])
        return Response({"user_tree": tree})


class UsersUpdateUsernamePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        users = User.objects.filter(deleted=False, user_roles=ORDINARY_USER, auth_status=DONE)
        new_data = []

        for user in users:
            old_username = user.username
            new_login = str(uuid4()).split("-")[-1]
            while User.objects.filter(username=new_login):
                new_login = f"rizon{str(uuid4()).split('-')[-1]}"
            user.username = new_login
            user.save()
            user_ser = UsersSerializer(user).data
            user_ser['old_username'] = old_username
            new_data.append(user_ser)

        return Response(new_data)


class UserGetAllInfoOldAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = User.objects.all()
    serializer_class = ForOthersUsersSerializer

    def get(self, request, *args, **kwargs):
        # forMentorship = mentorship_bonus_for_actives(user_id=kwargs['pk'], date=kwargs['date'])
        # user_all_bonus = user_all_bonuses_test(user_id=kwargs['pk'], date=kwargs['date'])
        user_all_bonus = user_all_bonuses2(user_id=kwargs['pk'], date=kwargs['date'])
        return Response(user_all_bonus)


class UsersTemplateView(View):
    def get(self, request):
        data = {"users": User.objects.filter(deleted=False, auth_status=DONE).order_by("last_name")}
        return render(request, "users.html", data)


class UsersTreeUpdateDateAPIViewMainPy(APIView):
    def get(self, request):
        users = User.objects.all()
        for user in users:
            UsersTree.objects.filter(invited=user).update(date=user.date)

        return Response(
            {
                "success": True,
                "message": "Tree has been updated."
            }
        )


class UserGetOneWithTeacher(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.filter(deleted=False)
    serializer_class = ForOthersUsersSerializer

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, user_id=kwargs['pk'])
        if request.user.is_staff:
            user_ser = UsersSerializer(user).data
            user_ser.pop("password")

            teacher = UsersTree.objects.filter(invited=user)
            if teacher:
                teacher_ser = UsersSerializer(teacher[0].offerer).data
                teacher_ser.pop("password")

            return Response(
                {
                    "user": user_ser,
                    "teacher": teacher_ser
                }
            )
        else:
            user_ser = ForOthersUsersSerializer(user)
            return Response(user_ser.data)


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUpSerializer


class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = self.request.user             # user ->
        code = self.request.data.get('code') # 4083

        self.check_verify(user, code)
        return Response(
            data={
                "success": True,
                "auth_status": user.auth_status,
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token']
            }
        )

    @staticmethod
    def check_verify(user, code):       # 12:03 -> 12:05 => expiration_time=12:05   12:04
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        print(verifies)
        if not verifies.exists():
            data = {
                "message": "Tasdiqlash kodingiz xato yoki eskirgan"
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True


class GetNewVerification(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_phone_code(user.phone_number, code)
        else:
            data = {
                "message": "Email yoki telefon raqami notogri"
            }
            raise ValidationError(data)

        return Response(
            {
                "success": True,
                "message": "Tasdiqlash kodingiz qaytadan jo'natildi."
            }
        )

    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                "message": "Kodingiz hali ishlatish uchun yaroqli. Biroz kutib turing"
            }
            raise ValidationError(data)


class ChangeUserInformationView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ChangeUserInformation
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        try:
            if User.objects.filter(passport=request.data.get("passport")):
                return Response({
                    "success": False,
                    "message": "Passport ma'lumotlari xato kiritildi."
                }, status=400)
        except:
            pass
        # if request.user.auth_status in (NEW, CODE_VERIFIED):
        #     try:
        #         teacher = kwargs.pop("user_id")
        #         UsersTree.objects.create(
        #             offerer=User.objects.get(user_id=teacher),
        #             invited=User.objects.get(username=request.user.username)
        #         )
        #     except:
        #         pass
        # try:
        #     teacher = kwargs.pop("user_id")
        # except:
        #     pass
        try:
            offerer = request.data.pop("user_id")
            user = get_object_or_404(UserConfirmation, user=request.user)
            offerer_user = get_object_or_404(User, user_id=offerer)
            invited_user = get_object_or_404(User, id=user.user.id)
            is_there = UsersTree.objects.filter(invited=invited_user)
            if list(is_there) == []:
                UsersTree.objects.create(
                    offerer=offerer_user,
                    invited=invited_user
                )
                new_offer_id = int("".join([str(random.randint(0, 10000) % 10) for _ in range(9)]))
                while User.objects.filter(user_id=new_offer_id):
                    new_offer_id = int(f"{new_offer_id}{random.randint(0, 9)}")

                request.data['user_id'] = new_offer_id
        except:
            return Response({
                "success": False,
                "message": "Taklif ID noto'g'ri"
            }, status=400)

        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        data = {
            'success': True,
            "message": "User updated successfully",
            'auth_status': self.request.user.auth_status,
        }
        return Response(data, status=200)

    def partial_update(self, request, *args, **kwargs):
        # if request.user.auth_status in (NEW, CODE_VERIFIED):
        #     try:
        #         teacher = kwargs.pop("user_id")
        #         UsersTree.objects.create(
        #             offerer=User.objects.get(user_id=teacher),
        #             invited=User.objects.get(username=request.user.username)
        #         )
        #     except:
        #         # teacher = kwargs.pop("user_id")
        #         # raise ValidationError({
        #         #     "success": False,
        #         #     "message": "Taklif egasi topilmadi.",
        #         #     "teacher_id": teacher
        #         # })
        #         pass
        # try:
        #     teacher = kwargs.pop("user_id")
        # except:
        #     pass
        # try:
        #     if User.objects.filter(passport=request.data.get("passport")):
        #         return Response({
        #             "success": False,
        #             "message": "Passport ma'lumotlari xato kiritildi."
        #         }, status=400)
        # except:
        #     pass
        try:
            if UsersTree.objects.filter(invited=request.user).exists():
                pass
            else:
                offerer = request.data.pop("user_id")
                user = get_object_or_404(UserConfirmation, user=request.user)
                offerer_user = get_object_or_404(User, user_id=offerer)
                invited_user = get_object_or_404(User, id=user.user.id)
                is_there = UsersTree.objects.filter(invited=invited_user)
                if list(is_there) == []:
                    UsersTree.objects.create(
                        offerer=offerer_user,
                        invited=invited_user
                    )
                    new_offer_id = int("".join([str(random.randint(0, 10000) % 10) for _ in range(9)]))
                    while User.objects.filter(user_id=new_offer_id):
                        new_offer_id = int(f"{new_offer_id}{random.randint(0, 9)}")

                    request.data['user_id'] = new_offer_id
        except:
            return Response({
                "success": False,
                "message": "Taklif ID noto'g'ri"
            }, status=400)

        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        data = {
            'success': True,
            "message": "User updated successfully",
            'auth_status': self.request.user.auth_status,
        }
        return Response(data, status=200)


class ChangeUserPhotoView(APIView):
    permission_classes = [IsAuthenticated, ]

    def put(self, request, *args, **kwargs):
        serializer = ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            return Response({
                'message': "Rasm muvaffaqiyatli o'zgartirildi"
            }, status=200)
        return Response(
            serializer.errors, status=400
        )


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogOutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                'success': True,
                'message': "You are loggout out"
            }
            return Response(data, status=205)
        except TokenError:
            return Response(status=400)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get('user')
        if check_email_or_phone(email_or_phone) == 'phone':
            code = user.create_verify_code(VIA_PHONE)
            send_phone_code(email_or_phone, code)
        elif check_email_or_phone(email_or_phone) == 'email':
            code = user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone, code)

        return Response(
            {
                "success": True,
                'message': "Tasdiqlash kodi muvaffaqiyatli yuborildi",
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token'],
                "user_status": user.auth_status,
            }, status=200
        )


class ResetPasswordView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).update(request, *args, **kwargs)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(detail='User not found')
        return Response(
            {
                'success': True,
                'message': "Parolingiz muvaffaqiyatli o'zgartirildi",
                'access': user.token()['access'],
                'refresh': user.token()['refresh_token'],
            }
        )

from users.models import *
############################################################################################################

def user_real_time_coupon(request):
    user_coupons = UserSalary.objects.filter(user=request.user).aggregate(Sum('coupon'))
    user_coupons_sum = user_coupons['coupon__sum'] if user_coupons['coupon__sum'] is not None else 0

    used_coupons = SalePromotion.objects.filter(user=request.user).aggregate(Sum('coupon'))
    used_coupons_sum = used_coupons['coupon__sum'] if used_coupons['coupon__sum'] is not None else 0

    transfered_coupons = CouponTransfer.objects.filter(sender=request.user).aggregate(Sum('used'))
    transfered_coupons_sum = transfered_coupons['used__sum'] if transfered_coupons['used__sum'] is not None else 0

    receivered_coupons = CouponTransfer.objects.filter(receiver=request.user).aggregate(Sum('used'))
    receivered_coupons_sum = receivered_coupons['used__sum'] if receivered_coupons['used__sum'] is not None else 0

    fine_coupons = UsersCoupon.objects.filter(user=request.user).aggregate(Sum('used'))
    fine_coupons_sum = fine_coupons['used__sum'] if fine_coupons['used__sum'] is not None else 0

    try:
        pending_coupon = UserSalary.objects.get(month__startswith=str(datetime.today())[:7])
        pending_coupon = pending_coupon.coupon
    except:
        pending_coupon = 0

    coupon = user_coupons_sum - used_coupons_sum - transfered_coupons_sum + receivered_coupons_sum - fine_coupons_sum - pending_coupon

    return coupon


def user_real_time_coupon_for_admin(user):
    user_coupons = UserSalary.objects.filter(user=user).aggregate(Sum('coupon'))
    user_coupons_sum = user_coupons['coupon__sum'] if user_coupons['coupon__sum'] is not None else 0

    used_coupons = SalePromotion.objects.filter(user=user).aggregate(Sum('coupon'))
    used_coupons_sum = used_coupons['coupon__sum'] if used_coupons['coupon__sum'] is not None else 0

    transfered_coupons = CouponTransfer.objects.filter(sender=user).aggregate(Sum('used'))
    transfered_coupons_sum = transfered_coupons['used__sum'] if transfered_coupons['used__sum'] is not None else 0

    receivered_coupons = CouponTransfer.objects.filter(receiver=user).aggregate(Sum('used'))
    receivered_coupons_sum = receivered_coupons['used__sum'] if receivered_coupons['used__sum'] is not None else 0

    fine_coupons = UsersCoupon.objects.filter(user=user).aggregate(Sum('used'))
    fine_coupons_sum = fine_coupons['used__sum'] if fine_coupons['used__sum'] is not None else 0

    try:
        pending_coupon = UserSalary.objects.get(month__startswith=str(datetime.today())[:7])
        pending_coupon = pending_coupon.coupon
    except:
        pending_coupon = 0

    coupon = user_coupons_sum - used_coupons_sum - transfered_coupons_sum + receivered_coupons_sum - fine_coupons_sum - pending_coupon

    return coupon


def user_header_totally_info(request, month: str):
    total_sales_Summa = WarehouseSaleProduct.objects.filter(user=request.user, dateTime__startswith=month).aggregate(Sum('summa'))
    total_sales_Summa = total_sales_Summa['summa__sum'] if total_sales_Summa['summa__sum'] is not None else 0
    try:
        total_sales_Summa = total_sales_Summa // rv_ball['BALL']
    except:
        total_sales_Summa = 0

    user_coupons = UserSalary.objects.filter(user=request.user).aggregate(Sum('coupon'))
    user_coupons_sum = user_coupons['coupon__sum'] if user_coupons['coupon__sum'] is not None else 0

    data = {
        "total_sales_summa": total_sales_Summa,
        "total_coupon": user_real_time_coupon(request),
        "total_ball": user_coupons_sum,
    }
    return data


def user_header_info(request, month: str):
    user = get_object_or_404(User, username=request.user.username)

    total_income = WarehouseSaleProduct.objects.filter(user=user, dateTime__startswith=month).aggregate(Sum('summa'))
    total_income_sum = total_income['summa__sum'] if total_income['summa__sum'] is not None else 0

    user_coupons = UserSalary.objects.filter(user=request.user).aggregate(Sum('coupon'))
    user_coupons_sum = user_coupons['coupon__sum'] if user_coupons['coupon__sum'] is not None else 0

    return  {
        "total_income": total_income_sum,
        "coupon": user_real_time_coupon(request),
        "ball": user_coupons_sum,
    }

class UserTreeGetInfo(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    # queryset = Users.objects.all()
    # serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        total_info = user_header_totally_info(request, kwargs['month'])
        tree = get_all_shajara(user_id=kwargs['pk'], month=kwargs['month'])
        total_info.update(
            {"user_tree": tree}
        )
        return Response(total_info)

        # tree = await get_all_shajara(user_id=kwargs['pk'], month=kwargs['month'])
        # return Response({"user_tree": tree})

# Users
# class UserTreeView(View):
#     def get(self, request, pk):
#         data = {"user_tree": shajara_malumotlari_2_0(user_id=pk)}
#         return render(request, "shajara.html", data)


class UserUpdateJoinedDateView(APIView):
    def get(self, request, user_id, date):
        User.objects.filter(user_id=user_id).update(date=date)
        user = get_object_or_404(User, user_id=user_id)
        user_ser = ForOthersUsersSerializer(user).data
        return Response(
            {
                "success": True,
                "message": "Muvaffaqiyatli",
                "user": user_ser,
                "updated_date": user_ser['date'],
            }
        )


# class UsersView(View):
#     def get(self, request):
#         data = {"users": Users.objects.filter(deleted=False).order_by("last_name")}
#         # users = Users.objects.all().order_by("last_name")
#
#         # users = Users.objects.filter(last_name__startswith="Al")
#         # users_ser = UsersSerializer(users, many=True)
#         #
#         # from dateutil import relativedelta
#         # from datetime import date
#         # month = str(date.today())
#         #
#         # m = date(year=int(month[:4]), month=int(month[5:7]), day=1)
#         # old_month = str(m - relativedelta.relativedelta(months=1))
#         #
#         # data = {}
#         # for user in users_ser.data:
#         #     data[user['id']] = user_all_bonuses2(user_id=user['id'], date=old_month)
#         return render(request, "users.html", data)


class UserTreeGetFirstTree(RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = User.objects.filter(deleted=False)
    serializer_class = UsersSerializer


    def get(self, request, *args, **kwargs):
        tree = UsersTree.objects.filter(offerer__id=kwargs['pk']).filter(deleted=False)
        tree_ser = UsersTreeSerializer(tree, many=True)
        return Response({"user_tree": tree_ser.data})


# class UserTreeGet(RetrieveAPIView):
#     permission_classes = [IsAuthenticated, IsAdminUser, ]
#     queryset = Users.objects.all()
#     serializer_class = UsersSerializer
#
#     def get(self, request, *args, **kwargs):
#         tree = get_user_tree(kwargs['pk'])
#         return Response({"user_tree": tree})


class UsersTransferData(APIView):

    def post(self, request):
        try:
            user = User.objects.create(
                username=request.data.get("username"),
                password=request.data.get("password"),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                passport=request.data.get("passport"),
                user_roles=ORDINARY_USER,
                auth_type=VIA_PHONE,
                auth_status=DONE,
                phone_number=request.data.get("phone_number"),
                user_id=request.data.get("user_id"),
                address=request.data.get("address"),
                phoneNumTwo=request.data.get("phoneNumTwo"),
                dateOfBirth=request.data.get("dateOfBirth"),
                date=request.data.get("date")
            )
            user_ser = ForOthersUsersSerializer(user).data
            return Response({
                "user": user_ser
            })
        except:
            return Response({
                "success": False,
                "user_id": f"{request.data.get('user_id')}",
                "message": "#################################################################################################################"+
                           "##################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "##########################################################"
            })


class UsersCreateFRBotAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)


    def post(self, request):
        try:
            user = User.objects.create(
                username=request.data.get("username"),
                password=request.data.get("password"),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                passport=request.data.get("passport"),
                user_roles=ORDINARY_USER,
                auth_type=VIA_PHONE,
                auth_status=DONE,
                phone_number=request.data.get("phone_number"),
                user_id=request.data.get("user_id"),
                address=request.data.get("address"),
                phoneNumTwo=request.data.get("phoneNumTwo"),
                dateOfBirth=request.data.get("dateOfBirth"),
            )
            UsersTree.objects.create(
                invited=user,
                offerer=User.objects.get(user_id=request.data.get("offerer_id"))
            )
            user_ser = ForAdminUsersSerializer(user).data
            return Response({
                "user": user_ser
            })
        except:
            return Response({
                "success": False,
                "user_id": f"{request.data.get('user_id')}",
                "message": "#################################################################################################################"+
                           "##################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "##########################################################"
            })


class BrandManagerCreateFRBotAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)


    def post(self, request):
        try:
            user = User.objects.create(
                username=request.data.get("username"),
                password=request.data.get("password"),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                passport=request.data.get("passport"),
                user_roles=BRAND_MANAGER,
                auth_type=VIA_PHONE,
                auth_status=DONE,
                phone_number=request.data.get("phone_number"),
                user_id=int(request.data.get("user_id")) + 1,
                address=request.data.get("address"),
                phoneNumTwo=request.data.get("phoneNumTwo"),
                dateOfBirth=request.data.get("dateOfBirth"),
            )

            user_ser = ForOthersUsersSerializer(user).data
            return Response({
                "success": True,
                "user": user_ser
            })
        except:
            return Response({
                "success": False,
                "user_id": f"{request.data.get('user_id')}",
                "message": "#################################################################################################################"+
                           "##################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "##########################################################"
            }, status=status.HTTP_400_BAD_REQUEST)


class BrandManagerDeleteFRBotAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    http_method_names = ("delete", )

    def delete(self, request, user_id):
        User.objects.filter(user_id=user_id).update(deleted=True)
        return Response(
            {
                "success": True,
                "message": "Brand manager ( admin ) has been deleted"
            }
        )


class UserUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)


    def post(self, request, user_id):
        try:
            User.objects.filter(user_id=user_id).update(
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                passport=request.data.get("passport"),
                phone_number=request.data.get("phone_number"),
                address=request.data.get("address"),
                phoneNumTwo=request.data.get("phoneNumTwo"),
                dateOfBirth=request.data.get("dateOfBirth"),
            )
            user = User.objects.get(user_id=user_id)
            user_ser = ForOthersUsersSerializer(user).data
            return Response({
                "success": True,
                "user": user_ser
            })
        except:
            return Response({
                "success": False,
                "user_id": f"{request.data.get('user_id')}",
                "message": "#################################################################################################################"+
                           "##################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "##########################################################"
            }, status=status.HTTP_400_BAD_REQUEST)


class UsersTreeTransferData(APIView):

    def post(self, request):
        try:
            user_Tree = UsersTree.objects.create(
                offerer=User.objects.get(username=request.data.get("offerer"),),
                invited=User.objects.get(username=request.data.get("invited")),
                date=request.data.get("date"),
            )
            user_tree_ser = UsersTreeSerializer(user_Tree).data
            return Response({
                "user_tree": user_tree_ser
            })
        except:
            return Response({
                "success": False,
                "offerer": f"{request.data.get('offerer')}",
                "invited": f"{request.data.get('invited')}",
                "message": "#################################################################################################################"+
                           "##################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "###################################################################################################################"+
                           "##########################################################"
            })


class UserGetOne(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.filter(deleted=False)
    serializer_class = ForOthersUsersSerializer


    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, user_id=kwargs['pk'])
        if request.user.is_staff:
            user_ser = UsersSerializer(user).data
            user_ser.pop("password")
            return Response(user_ser)
        else:
            user_ser = ForOthersUsersSerializer(user)
            return Response(user_ser.data)


class UserGetAllInfo(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = User.objects.all()
    serializer_class = ForOthersUsersSerializer

    def get(self, request, *args, **kwargs):
        # forMentorship = mentorship_bonus_for_actives(user_id=kwargs['pk'], date=kwargs['date'])
        user_all_bonus = user_all_bonuses_test(user_id=kwargs['pk'], date=kwargs['date'])

        # transfer_users()
        # transfer_tree()
        # transfer_products()
        # transfer_medics()
        # transfer_medics_product()
        # transfer_employee()
        # transfer_sales_data()
        # transfer_sales_data3()

        return Response(user_all_bonus)

# class UserGetAllInfo2222222222(RetrieveAPIView):
#     permission_classes = [IsAuthenticated, IsAdminUser, ]
#     queryset = User.objects.all()
#     serializer_class = ForOthersUsersSerializer
#
#     def get(self, request, *args, **kwargs):
#         user_coupon_sum = UsersCoupon.objects.filter(user__id=kwargs['pk']).aggregate(Sum('used'))  # , dateTime__startswith=kwargs['date']
#         user = User.objects.get(id=kwargs['pk'])
#         user_ser = ForOthersUsersSerializer(user)
#
#         months = pd.period_range(str(user_ser.data['date'])[:7], str(datetime.today())[:7], freq='M')[::-1][1:]
#         exist = 0
#
#         user = {}
#
#         for m in months:
#             user_all_bonus = user_all_bonuses2(user_id=kwargs['pk'], date=str(m))
#             exist += user_all_bonus['coupon']
#
#             if str(m).startswith(kwargs['date']):
#                 user = user_all_bonus
#
#         if user_coupon_sum['used__sum'] is not None:
#             return Response({"user_salary": user, "used": user_coupon_sum['used__sum'], "exist": exist - user_coupon_sum['used__sum']})
#         else:
#             return Response({"user_salary": user, "used": 0, "exist": exist})
#
#         # user_all_bonus = user_all_bonuses2(user_id=kwargs['pk'], date=kwargs['date'])
#
#         # return Response(user_all_bonus)


class UsersGetSalesByDate(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        sales = WarehouseSaleProduct.objects.filter(user__id=kwargs['pk'], dateTime__gte=kwargs['startDate']).filter(dateTime__lte=kwargs['endDate']).aggregate(Sum('summa'))
        if sales['summa__sum'] is not None:
            return Response({"sales_sum": sales['summa__sum']})
        return Response({"sales_sum": 0})


class UsersGetLastSale(RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        sales = WarehouseSaleProduct.objects.filter(user__id=str(kwargs['pk'])).order_by("-dateTime")
        sales_ser = WarehouseSaleProductSerializer(sales, many=True).data

        if sales_ser:
            return Response({"last_sale": sales_ser[0]})
        return Response({"last_sale": {"id": 1, "dateTime": "str"}})



class UsersListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = User.objects.filter(user_roles=ORDINARY_USER, auth_status=DONE)
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            users = User.objects.filter(deleted=False, user_roles=ORDINARY_USER, auth_status=DONE).order_by("last_name")
            users_ser = UsersSerializer(users, many=True)
            return Response({"users": users_ser.data})
        else:
            return Response({"detail": "You are not provided this action"})


class UsersGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.filter(deleted=False)
    serializer_class = UsersSerializer

    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            User.objects.filter(id=kwargs['pk']).update(deleted=True)
            return Response({"detail": "deleted"})
        else:
            return Response({"detail": "You are not provided this action"})


# UsersTree
# class UsersTreeListCreate(ListCreateAPIView):
#     permission_classes = [IsAuthenticated, IsAdminUser, ]
#     queryset = UsersTree.objects.all()
#     serializer_class = UsersTreeSerializer
#
#     def create(self, request, *args, **kwargs):
#         ser = PostUsersTreeSerializer(data=request.data)
#         if ser.is_valid():
#             ser.save()
#             return Response(ser.data)
#         else:
#             return Response(ser.errors)


# class UsersTreeGetUpdateDelete(RetrieveAPIView):
#     permission_classes = [IsAuthenticated, IsAdminUser, ]
#     queryset = UsersTree.objects.all()
#     serializer_class = UsersTreeSerializer



# UsersSalary
class UsersSalaryListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsEmployee ]
    queryset = UsersSalaryPayment.objects.all()
    serializer_class = UsersSalarySerializer


    def post(self, request, *args, **kwargs):
        ser = PostUsersSalarySerializer2(data=request.data)
        if ser.is_valid():
            employee = get_object_or_404(Employee, user=request.user)
            UsersSalaryPayment.objects.create(
                salary_payer=employee.warehouse,
                user=User.objects.get(id=ser.data.get("user")),
                paid=ser.data.get("paid"),
                date=str(request.data.get("date"))+"-10"
            )
            return Response(ser.data)
        else:
            return Response(ser.errors)


class UsersSalaryGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = UsersSalaryPayment.objects.all()
    serializer_class = UsersSalarySerializer


class UsersSalaryGetPayments(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsEmployee]
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['pk'])
        salary_history = UserSalary.objects.filter(user=user)
        salary_history_ser = UserSalarySerializer(salary_history, many=True).data

        return Response({
            "payments": salary_history_ser
        })


# UsersCoupon
class UsersCouponUsedSum(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        user_coupon_sum = UsersCoupon.objects.filter(user__id=kwargs['pk']).aggregate(Sum('used'))
        user = User.objects.get(id=kwargs['pk'])
        coupon = user_real_time_coupon_for_admin(user)

        user_coupon_sum = user_coupon_sum['used__sum'] if user_coupon_sum['used__sum'] is not None else 0
        return Response({"used": user_coupon_sum, "exist": coupon})


class UsersCouponUsedSumForUser(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.filter(deleted=False)
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        coupon = user_real_time_coupon_for_admin(user)
        user_coupon_sum = UsersCoupon.objects.filter(user=user).aggregate(Sum('used'))

        user_coupon_sum = user_coupon_sum['used__sum'] if user_coupon_sum['used__sum'] is not None else 0
        return Response({"used": user_coupon_sum, "exists": coupon})


# UsersCoupon
class UsersCouponListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = UsersCoupon.objects.all()
    serializer_class = UsersCouponSerializer


    def create(self, request, *args, **kwargs):
        ser = PostUsersCouponSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        else:
            return Response(ser.errors)

# class UsersCouponCreate(CreateAPIView):
#     queryset = UsersCoupon.objects.all()
#     serializer_class = PostUsersCouponSerializer
#
#     def post(self, request, *args, **kwargs):
#         all_coupon = 0
#         user = Users.objects.get(id=kwargs['user_id'])
#         from datetime import datetime
#         bu_oy = str(datetime.today())[:7]
#         user_data =
#         return Response({"error": "error"})


class UsersCouponGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = UsersCoupon.objects.all()
    serializer_class = UsersCouponSerializer


class UserMainPageAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data
        info = user_header_info(request, str(datetime.today())[:7])

        salary_payments = UsersSalaryPayment.objects.filter(user=user)
        salary_payments_ser = UsersSalarySerializer(salary_payments, many=True).data

        salary_data = {}

        for payment in salary_payments_ser:
            if str(payment["paymentDate"]) not in salary_data:
                salary_data[f"{payment['paymentDate']}"] = payment['paid']
            else:
                salary_data[f"{payment['paymentDate']}"] += payment['paid']

        discount_products = ProductDiscount.objects.filter(endDate__gte=datetime.today())
        discount_products_Ser = forLandiingPoductSerializer(discount_products, many=True)

        discounts = []

        for product in discount_products_Ser:
            product['discount'] = f"{product['amount']}+{product['discount']} aksiya"
            product['lifetime'] = f"Chegirma muddati {str(product['startDate'])[:10]} sanasidan {str(product['endDate'])[:10]} sanasiga qadar davom etadi."
            discounts.append(product)
        month_product_sales_data2 = []
        month_product_sales_data = {}
        products_data = Product.objects.filter(deleted=False)
        products_data_ser = ProductSerializer(products_data, many=True).data
        month_product_sales = WarehouseSaleProduct.objects.filter(user=request.user).aggregate(Sum('amount'))
        product_sale_amount_divide = month_product_sales['amount__sum'] if month_product_sales['amount__sum'] is not None else 1

        for product in products_data_ser:
            product_sale_amount = WarehouseSaleProduct.objects.filter(product=product['id'], user=request.user).aggregate(Sum('amount'))
            product_sale_amount = product_sale_amount['amount__sum'] if product_sale_amount['amount__sum'] is not None else 0
            product_sale_summa = WarehouseSaleProduct.objects.filter(product=product['id'], user=request.user).aggregate(Sum('summa'))
            product_sale_summa = product_sale_summa['summa__sum'] if product_sale_summa['summa__sum'] is not None else 0

            try:
                percent_p = round(product_sale_amount / product_sale_amount_divide * 100, 1)
            except:
                percent_p = 0

            month_product_sales_data[f"{product['name']}"] = {"product_sales_percent": percent_p, 'product_sale_amount': product_sale_amount, 'product_sale_summa': product_sale_summa}
            month_product_sales_data2.append({"name": f"{product['name']}", "product_sales_percent": percent_p, 'product_sale_amount': product_sale_amount, 'product_sale_summa': product_sale_summa})

        info.update({
            "salary_data": salary_data,
            "product_sales_data": month_product_sales_data,
            "product_sales_data2": month_product_sales_data2,
            "discounts": discounts,
            "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
            "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}"
        })

        return Response(info)


class UserMainPageAPIAndroid(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data
        info = user_header_info(request, str(datetime.today())[:7])

        salary_payments = UsersSalaryPayment.objects.filter(user=user)
        salary_payments_ser = UsersSalarySerializer(salary_payments, many=True).data

        salary_data = {}

        for payment in salary_payments_ser:
            if str(payment["paymentDate"]) not in salary_data:
                salary_data[f"{payment['paymentDate']}"] = payment['paid']
            else:
                salary_data[f"{payment['paymentDate']}"] += payment['paid']

        salary_data_new = []
        for k, v in salary_data.items():
            salary_data_new.append({
                "date": k,
                "paid": v,
            })

        discount_products = ProductDiscount.objects.filter(endDate__gte=datetime.today())
        discount_products_Ser = forLandiingPoductSerializer(discount_products, many=True)

        discounts = []

        for product in discount_products_Ser:
            product['discount'] = f"{product['amount']}+{product['discount']} aksiya"
            product['lifetime'] = f"Chegirma muddati {str(product['startDate'])[:10]} sanasidan {str(product['endDate'])[:10]} sanasiga qadar davom etadi."
            discounts.append(product)

        month_product_sales_data = []
        products_data = Product.objects.filter(deleted=False)
        products_data_ser = ProductSerializer(products_data, many=True).data
        month_product_sales = WarehouseSaleProduct.objects.filter(user=request.user).aggregate(Sum('amount'))
        product_sale_amount_divide = month_product_sales['amount__sum'] if month_product_sales['amount__sum'] is not None else 1

        for product in products_data_ser:
            product_sale_amount = WarehouseSaleProduct.objects.filter(product=product['id'], user=request.user).aggregate(Sum('amount'))
            product_sale_amount = product_sale_amount['amount__sum'] if product_sale_amount['amount__sum'] is not None else 0
            product_sale_summa = WarehouseSaleProduct.objects.filter(product=product['id'], user=request.user).aggregate(Sum('summa'))
            product_sale_summa = product_sale_summa['summa__sum'] if product_sale_summa['summa__sum'] is not None else 0

            try:
                percent_p = round(product_sale_amount / product_sale_amount_divide * 100, 1)
            except:
                percent_p = 0

            month_product_sales_data.append({"name": f"{product['name']}", "product_sales_percent": percent_p, 'product_sale_amount': product_sale_amount, 'product_sale_summa': product_sale_summa})

        info.update({
            "salary_data": salary_data_new,
            "product_sales_data": month_product_sales_data,
            "discounts": discounts,
            "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
            "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}"
        })

        return Response(info)


class UserProductPageAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data

        products_data = Product.objects.filter(deleted=False)
        products_data_ser = ProductSerializer(products_data, many=True).data

        discount_products = ProductDiscount.objects.filter(endDate__gte=datetime.today())
        discount_products_Ser = forLandiingPoductSerializer(discount_products, many=True)

        discounts = []

        for product in discount_products_Ser:
            product['discount'] = f"{product['amount']}+{product['discount']} aksiya"
            product['lifetime'] = f"Chegirma muddati {str(product['startDate'])[:10]} sanasidan {str(product['endDate'])[:10]} sanasiga qadar davom etadi."
            discounts.append(product)

        return Response({
            "products": products_data_ser,
            "discounts": discounts,
            "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
            "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}"
        })


class UserOrdersPageAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data

        total_orders = ProductOrder.objects.filter(user=user).count()
        active_orders = ProductOrder.objects.filter(user=user, done=False).count()
        orders = ProductOrder.objects.filter(user=user, done=False)
        orders_ser = ProductOrderSerializer(orders, many=True).data

        sales_history = WarehouseSaleProduct.objects.filter(user=user)
        sales_history_ser = WarehouseSaleProductSerializer(sales_history, many=True).data

        orders_data = []

        for order in orders_ser:
            order['summa'] = order['amount'] * order['product']['price']
            orders_data.append(order)

        return Response({
            "total_orders": total_orders,
            "active_orders": active_orders,
            "orders": orders_data,
            "sales_history": sales_history_ser,
            "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
            "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}"
        })


class UserNotificationsAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data

        notifications = UserNotification.objects.filter(user=request.user).order_by("date")
        notifications_ser = UserNotificationSerializers(notifications, many=True).data

        # UserNotification.objects.create(
        #     user=user,
        #     message=request.data.get("message"),
        #     title=request.data.get("title")
        # )

        return Response({
            "notifications": notifications_ser[::-1],
            "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
            "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}"
        })


class UserProfileAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data
        user = user_all_bonuses_test(user_id=user_ser['id'], date=str(kwargs['month'])[:7])

        tree = get_all_shajara(user_id=user_ser['id'], month=f"{str(kwargs['month'])[:7]}-04 10:34:04.860226")

        return Response(
            {
                "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
                "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}",
                "user": user,
                "user_tree": tree,
            }
        )



class UserProfileAPIAndroid(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data
        user = user_all_bonuses_test(user_id=user_ser['id'], date=str(kwargs['month'])[:7])

        tree = get_all_shajara(user_id=user_ser['id'], month=f"{str(kwargs['month'])[:7]}-04 10:34:04.860226")

        return Response(
            {
                "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
                "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}",
                "user": user,
                "user_tree": tree.values(),
            }
        )


class UserSalaryHistory(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['pk'])
        history = UsersSalaryPayment.objects.filter(user=user)
        history_ser = UsersSalarySerializer(history, many=True).data

        return Response({
            "salary_history": history_ser
        })

class UserSalaryHistory2(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        # user_ser = UsersSerializer(user).data
        # history = UsersSalaryPayment.objects.filter(user=user)
        # history_ser = UsersSalarySerializer(history, many=True).data
        # filiallar = [
        #     {
        #         "id": 2,
        #         "name": "To'rtko'l",
        #         "address": "To'rtko'l sh. Bozor hududida 392 do'kon",
        #         "phone": "+998913011539",
        #         "photo": "http://rizonwebapp.pythonanywhere.com/media/warehouse_photos/images.jfif",
        #         "about": "Rizon kompaniyasi filiali"
        #     },
        #     {
        #         "id": 3,
        #         "name": "Qo'qon",
        #         "address": "Qo'qon sh. Yo'lkobod 24",
        #         "phone": "+998999910005",
        #         "photo": "http://rizonwebapp.pythonanywhere.com/media/warehouse_photos/images_1.jfif",
        #         "about": "Rizon kompaniyasi filiali"
        #     },
        #     {
        #         "id": 4,
        #         "name": "Toshkent",
        #         "address": "Toshkent shahar, Shayhontoxur t-ni, Beruniy 1, 2-uy\r\n\r\nMo'ljal: Tinchlik metrosi",
        #         "phone": "+998330403030",
        #         "photo": "http://rizonwebapp.pythonanywhere.com/media/warehouse_photos/M%C3%BCnster_LVM_B%C3%BCrogeb%C3%A4ude_--_2013_--_5149-51.jpg",
        #         "about": "Rizon kompaniyasi filiali"
        #     },
        #     {
        #         "id": 5,
        #         "name": "Bosh Filial",
        #         "address": "Farg'ona vil. Farg'ona sh.",
        #         "phone": "+998950813000",
        #         "photo": "http://rizonwebapp.pythonanywhere.com/media/warehouse_photos/832__85_953886762.jpg",
        #         "about": "Rizon kompaniyasi filiali"
        #     }
        # ]
        #
        # filial = random.choice(filiallar)
        #
        # data = {
        #     "user": user_ser,
        #     "user_status": "Konsultant",
        #     "user_score": 50.0,
        #     "user_tree_score": 1145.0,
        #     "user_tree_summa": 17175000,
        #     "personal_bonus": 38500.0,
        #     "extra_bonus": 0,
        #     "coupon": 1145.0,
        #     "forMentorship": 160500,
        #     "bonus_for_followers_status": 100000,
        #     "collective_bonus_amount": 35000.0,
        #     "stat_percent": 10,
        #     "for_followers_status_percent": 0,
        #     "salary": 334000.0,
        #     "paid": 335000,
        #     "debt": 335000,
        #     "date": "2023-05-05",
        #     "paymentDate": "2023-05-05",
        #     "salary_payer": filial
        # }
        #
        # salary_history = []
        #
        # for i in range(10):
        #     salary_history.append(data)
        salary_history = UserSalary.objects.filter(user=request.user)
        salary_history_ser = UserSalarySerializer(salary_history, many=True).data

        return Response({
            "salary_history": salary_history_ser
        })


class UserSalaryPayGet(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['pk'])
        # user_ser = UsersSerializer(user).data
        salary = user_all_bonuses_test(user_id=user.id, date=kwargs['month'])

        # history = UsersSalaryPayment.objects.filter(user=user)
        # history_ser = UsersSalarySerializer(history, many=True).data
        # filiallar = [
        #     {
        #         "id": 2,
        #         "name": "To'rtko'l",
        #         "address": "To'rtko'l sh. Bozor hududida 392 do'kon",
        #         "phone": "+998913011539",
        #         "photo": "http://rizonwebapp.pythonanywhere.com/media/warehouse_photos/images.jfif",
        #         "about": "Rizon kompaniyasi filiali"
        #     },
        #     {
        #         "id": 3,
        #         "name": "Qo'qon",
        #         "address": "Qo'qon sh. Yo'lkobod 24",
        #         "phone": "+998999910005",
        #         "photo": "http://rizonwebapp.pythonanywhere.com/media/warehouse_photos/images_1.jfif",
        #         "about": "Rizon kompaniyasi filiali"
        #     },
        #     {
        #         "id": 4,
        #         "name": "Toshkent",
        #         "address": "Toshkent shahar, Shayhontoxur t-ni, Beruniy 1, 2-uy\r\n\r\nMo'ljal: Tinchlik metrosi",
        #         "phone": "+998330403030",
        #         "photo": "http://rizonwebapp.pythonanywhere.com/media/warehouse_photos/M%C3%BCnster_LVM_B%C3%BCrogeb%C3%A4ude_--_2013_--_5149-51.jpg",
        #         "about": "Rizon kompaniyasi filiali"
        #     },
        #     {
        #         "id": 5,
        #         "name": "Bosh Filial",
        #         "address": "Farg'ona vil. Farg'ona sh.",
        #         "phone": "+998950813000",
        #         "photo": "http://rizonwebapp.pythonanywhere.com/media/warehouse_photos/832__85_953886762.jpg",
        #         "about": "Rizon kompaniyasi filiali"
        #     }
        # ]
        #
        # filial = random.choice(filiallar)
        #
        # data = {
        #     "user": user_ser,
        #     "user_status": "Konsultant",
        #     "user_score": 50.0,
        #     "user_tree_score": 1145.0,
        #     "user_tree_summa": 17175000,
        #     "personal_bonus": 38500.0,
        #     "extra_bonus": 0,
        #     "coupon": 1145.0,
        #     "forMentorship": 160500,
        #     "bonus_for_followers_status": 100000,
        #     "collective_bonus_amount": 35000.0,
        #     "stat_percent": 10,
        #     "for_followers_status_percent": 0,
        #     "salary": 334000.0,
        #     # "paid": 335000,
        #     # "debt": 335000,
        #     # "date": "2023-05-05",
        #     # "paymentDate": "2023-05-05",
        #     "salary_payer": filial
        # }

        return Response({
            "salary": salary
        })



class UsersCouponTransferCreateAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = get_object_or_404(User, username=request.user.username)
        ser = PostCouponTransferSerializer(data=request.data)
        coupon = user_real_time_coupon(request)

        if ser.is_valid():
            if int(request.data.get("used")) >= 1000 and coupon >= 6000:
                CouponTransfer.objects.create(
                    sender=user,
                    comment=ser.data.get("comment"),
                    used=ser.data.get("used"),
                    receiver=get_object_or_404(User, id=ser.data.get("receiver"))
                )
                return Response({
                    "success": True,
                    "transfer": ser.data
                })
            else:
                return Response({
                    "success": False,
                    "message": "Transferning minimum miqdori 1000 kupon va shaxsiy kuponingiz minimum 6000 kupon bo'lishi shart"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "success": False,
                "message": f"Kupon transferida xatolikka yo'l qo'yildi !\n\n{ser.errors}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        send_transfers = CouponTransfer.objects.filter(sender=user)
        send_transfers_ser = CouponTransferSerializer(send_transfers, many=True).data

        income_transfers = CouponTransfer.objects.filter(receiver=user)
        income_transfers_ser = CouponTransferSerializer(income_transfers, many=True).data

        return Response({
            "transfers": send_transfers_ser + income_transfers_ser,
        })


class UserCouponsPageAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data
        user_ser.update({
            "coupon": user_real_time_coupon(request),
        })

        send_transfers = CouponTransfer.objects.filter(sender=user)
        send_transfers_ser = CouponTransferSerializer(send_transfers, many=True).data

        income_transfers = CouponTransfer.objects.filter(receiver=user)
        income_transfers_ser = CouponTransferSerializer(income_transfers, many=True).data

        # send_transfers_ser.update(income_transfers_ser)

        return Response({
            "transfers": send_transfers_ser + income_transfers_ser,
            "user": user_ser,
            "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
            "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}"
        })


class UsersCouponTransferGetAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        send_transfers = CouponTransfer.objects.get(id=kwargs['pk'])
        transfer = CouponTransferSerializer(send_transfers).data

        if transfer['sender']['username'] == user.username or transfer['receiver']['username'] == user.username:

            return Response({
                transfer
            })

        else:
            return ValidationError({
                "success": False,
                "message": "Siz ushbu amaliyotni bajarish huquqiga ega emassiz !"
            })

class UserSalesAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        sales = WarehouseSaleProduct.objects.filter(user=user)

        sales_ser = WarehouseSaleProductSerializer(sales, many=True).data

        return Response(sales_ser)



class UsersPromotionPageAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = Promotion.objects.filter(deleted=False, pause=False)
    serializer_class = PromotionSerializer

    def get(self, request, *args, **kwargs):
        max_coupon = Promotion.objects.aggregate(Max('coupon'))

        step1 = max_coupon['coupon__max'] // 3 if max_coupon['coupon__max'] is not None else 0
        step2 = max_coupon['coupon__max'] // 2 if max_coupon['coupon__max'] is not None else 0

        min_promotions = Promotion.objects.filter(coupon__lte=step1).filter(deleted=False, pause=False)
        min_promotions_ser = PromotionSerializer(min_promotions, many=True).data

        avg_promotions = Promotion.objects.filter(coupon__gt=step1).filter(coupon__lte=step2).filter(deleted=False, pause=False)
        avg_promotions_ser = PromotionSerializer(avg_promotions, many=True).data

        max_promotions = Promotion.objects.filter(coupon__gt=step2).filter(deleted=False, pause=False)
        max_promotions_ser = PromotionSerializer(max_promotions, many=True).data

        min_promotions_ser_data = []
        avg_promotions_ser_data = []
        max_promotions_ser_data = []

        for min_p in min_promotions_ser:
            sold = SalePromotion.objects.filter(promotion__id=min_p['id']).aggregate(Sum('amount'))
            amount = PromotionAmount.objects.filter(promotion__id=min_p['id']).aggregate(Sum('amount'))

            sold = sold['amount__sum'] if sold['amount__sum'] is not None else 0
            amount = amount['amount__sum'] if amount['amount__sum'] is not None else 0

            min_p['amount'] = amount - sold
            min_promotions_ser_data.append(min_p)

        for avg_p in avg_promotions_ser:
            sold = SalePromotion.objects.filter(promotion__id=avg_p['id']).aggregate(Sum('amount'))
            amount = PromotionAmount.objects.filter(promotion__id=avg_p['id']).aggregate(Sum('amount'))

            sold = sold['amount__sum'] if sold['amount__sum'] is not None else 0
            amount = amount['amount__sum'] if amount['amount__sum'] is not None else 0

            avg_p['amount'] = amount - sold
            avg_promotions_ser_data.append(avg_p)

        for max_p in max_promotions_ser:
            sold = SalePromotion.objects.filter(promotion__id=max_p['id']).aggregate(Sum('amount'))
            amount = PromotionAmount.objects.filter(promotion__id=max_p['id']).aggregate(Sum('amount'))

            sold = sold['amount__sum'] if sold['amount__sum'] is not None else 0
            amount = amount['amount__sum'] if amount['amount__sum'] is not None else 0

            max_p['amount'] = amount - sold
            max_promotions_ser_data.append(max_p)

        try:
            pending_coupon = UserSalary.objects.get(month__startswith=str(datetime.today())[:7])
            pending_coupon = pending_coupon.coupon
        except:
            pending_coupon = 0

        return Response({
            "coupon": user_real_time_coupon(request),
            "pending_coupon": pending_coupon,
            "small_interval": min_promotions_ser_data,
            "middle_interval": avg_promotions_ser_data,
            "large_interval": max_promotions_ser_data
        })

class UsersPromotionPurchasesPageAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    # queryset = Promotion.objects.filter(deleted=False, pause=False)
    # serializer_class = PromotionSerializer

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data

        history = SalePromotion.objects.filter(user=request.user)
        history_Ser = SalePromotionSerializer(history, many=True).data

        return Response({
            "coupon": user_real_time_coupon(request),
            "purchases": history_Ser,
            "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
            "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}"
        })


class UsersPromotionPurchasesAPIView(APIView):
    permission_classes = [IsAuthenticated, ]


    def get(self, request):
        print(f"{request.data=}")
        print(f"{request=}")
        user = get_object_or_404(User, username=request.user.username)
        user_ser = ForOthersUsersSerializer(user).data

        history = SalePromotion.objects.filter(user=request.user)
        history_Ser = SalePromotionSerializer(history, many=True).data

        return Response({
            "coupon": user_real_time_coupon(request),
            "purchases": history_Ser,
            "sale_link": f"https://t.me/rizonuz_dokon_bot?start={user_ser['user_id']}",
            "follower_link": f"https://t.me/rizonuzbot?start={user_ser['user_id']}"
        })


class UsersPromotionGetAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, **kwargs):
        promotion = get_object_or_404(Promotion, id=kwargs['pk'])
        promotion_Ser = PromotionSerializer(promotion).data
        return Response(
            promotion_Ser
        )


class CheckPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, **kwargs):
        user = User.objects.filter(passport=kwargs['passport'])

        if user.exists() == True:
            return Response(
                {
                    "success": True,
                    "message": "This passport information is already registered."
                }
            )
        return Response(
            {
                "success": False,
                "message": "Not found"
            }, status=status.HTTP_400_BAD_REQUEST
        )


class UsersPromotionBuyAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    # queryset = SalePromotion.objects.filter(deleted=False, pause=False)
    # serializer_class = PostSalePromotionSerializer

    # def create(self, request, *args, **kwargs):
    #     ser = PostSalePromotionSerializer(data=request.data)
    #     if ser.is_valid():
    #         user = get_object_or_404(User, username=request.user.username)
    #         coupon = user_real_time_coupon(request)
    #
    #         promotion = Promotion.objects.get(id=ser.data.get("promotion"))
    #         promotion_ser = PromotionSerializer(promotion).data
    #         promo_coupon = promotion_ser['coupon'] * ser.data.get("amount")
    #
    #         if promo_coupon <= coupon:
    #             purchase = SalePromotion.objects.create(
    #                 promotion = promotion,
    #                 user = user,
    #                 amount = ser.data.get("amount"),
    #                 coupon = promo_coupon
    #             )
    #             return Response({
    #                 "success": True,
    #                 "message": "Promotion muvaffaqiyatli harid qilindi. Haridni 3 kun ichida topshiramiz !",
    #                 "purchase": purchase
    #             })
    #
    #         else:
    #             return Response({
    #                 "success": False,
    #                 "message": "Afsuski ushbu Promotion'ni sotib olish uchun sizda yetarli kupon mavjud emas !",
    #             })
    #     else:
    #         return Response(ser.errors)

    def post(self, request, *args, **kwargs):
        ser = PostSalePromotionSerializer(data=request.data)
        if ser.is_valid():
            user = get_object_or_404(User, username=request.user.username)
            coupon = user_real_time_coupon(request)

            promotion = Promotion.objects.get(id=ser.data.get("promotion"))
            promotion_ser = PromotionSerializer(promotion).data
            promo_coupon = promotion_ser['coupon'] * ser.data.get("amount")

            if promo_coupon <= coupon:
                purchase = SalePromotion.objects.create(
                    promotion = promotion,
                    user = user,
                    amount = ser.data.get("amount"),
                    coupon = promo_coupon
                )
                purchase = SalePromotionSerializer(purchase).data
                return Response({
                    "success": True,
                    "message": "Promotion muvaffaqiyatli harid qilindi. Haridni 3 kun ichida topshiramiz !",
                    "purchase": purchase
                })

            else:
                return Response({
                    "success": False,
                    "message": "Afsuski ushbu Promotion'ni sotib olish uchun sizda yetarli kupon mavjud emas !",
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(ser.errors)


def usersPromotionBuyAPIViewFunc(request):
    if request.method == "POST":
        ser = PostSalePromotionSerializer(data=request.data)
        if ser.is_valid():
            user = get_object_or_404(User, username=request.user.username)
            coupon = user_real_time_coupon(request)

            promotion = Promotion.objects.get(id=ser.data.get("promotion"))
            promotion_ser = PromotionSerializer(promotion).data
            promo_coupon = promotion_ser['coupon'] * ser.data.get("amount")

            if promo_coupon <= coupon:
                purchase = SalePromotion.objects.create(
                    promotion = promotion,
                    user = user,
                    amount = ser.data.get("amount"),
                    coupon = promo_coupon
                )
                return Response({
                    "success": True,
                    "message": "Promotion muvaffaqiyatli harid qilindi. Haridni 3 kun ichida topshiramiz !",
                    "purchase": purchase
                })

            else:
                return Response({
                    "success": False,
                    "message": "Afsuski ushbu Promotion'ni sotib olish uchun sizda yetarli kupon mavjud emas !",
                })
        else:
            return Response(ser.errors)


class UsersProductDiscountAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        total_info = user_header_totally_info(request, "20")

        discounts = ProductDiscount.objects.filter(endDate__gte=str(datetime.today()))
        # discounts = ProductDiscount.objects.all()
        discounts_Ser = ProductDiscountSerializer(discounts, many=True).data

        discounts_data = []

        for disc in discounts_Ser:
            sold = WarehouseSaleProduct.objects.filter(product__id=disc['product']['id'], dateTime__gte=disc['startDate']).filter(dateTime__lte=disc['endDate']).aggregate(Sum('amount'))
            disc['sold'] = sold['amount__sum'] if sold['amount__sum'] is not None else 0
            discounts_data.append(disc)

        total_info.update({
            "dicounts": discounts_data
        })

        return Response(total_info)



class UserSalaryPaymentsTransferView(APIView):

    def post(self, request):
        data = request.data
        try:
            payment = UsersSalaryPayment.objects.create(
                salary_payer=Warehouse.objects.get(phone=data['warehouse']),
                user=User.objects.get(username=data['user']),
                paid=data['paid'],
                date=data['date'],
                paymentDate=data['paymentDate']
            )
            payment_ser = UsersSalarySerializer(payment).data
            return Response(payment_ser)
        except:
            return Response(
                {
                    "success": False,
                    "message": "################" * 30
                }
            )


class GetUsersCouponsSumFRBot(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request):
        users = User.objects.filter(auth_status=DONE)
        users_data = []
        for user in users:
            user_coupon = user_real_time_coupon_for_admin(user)
            if user_coupon > 0:
                users_data.append(
                    {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "user_id": user.user_id,
                        "phone_number": user.phone_number,
                        "coupon": user_coupon,
                    }
                )

        return Response(users_data)


class UserBonusAccounts(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = request.user
        bonuses_history = BonusAccount.objects.filter(user=user).order_by('-created_time')
        history_ser = BonusAccountSerializer(bonuses_history, many=True).data

        cashback = BonusAccount.objects.filter(user=user, bonus_type=CASHBACK).aggregate(Sum('amount'))
        cashback_sum = cashback['amount__sum'] if cashback['amount__sum'] is not None else 0
        voucher = BonusAccount.objects.filter(user=user, bonus_type=VOUCHER).aggregate(Sum('amount'))
        voucher_sum = voucher['amount__sum'] if voucher['amount__sum'] is not None else 0
        travel = BonusAccount.objects.filter(user=user, bonus_type=TRAVEL).aggregate(Sum('amount'))
        travel_sum = travel['amount__sum'] if travel['amount__sum'] is not None else 0
        umrah = BonusAccount.objects.filter(user=user, bonus_type=UMRAH).aggregate(Sum('amount'))
        umrah_sum = umrah['amount__sum'] if umrah['amount__sum'] is not None else 0
        autobonus = BonusAccount.objects.filter(user=user, bonus_type=AUTOBONUS).aggregate(Sum('amount'))
        autobonus_sum = autobonus['amount__sum'] if autobonus['amount__sum'] is not None else 0

        return Response(
            {
                CASHBACK: cashback_sum,
                VOUCHER: voucher_sum,
                TRAVEL: travel_sum,
                UMRAH: umrah_sum,
                AUTOBONUS: autobonus_sum,
                "history": history_ser
            }
        )


class UndeleteUsersApiView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.filter(deleted=True)
        deleted_users = []
        for user in users:
            try:
                user.phone_number = user.phoneNumTwo
                user.deleted = False
                user.save()
            except Exception as e:
                deleted_users.append(user.user_id)
        return Response(
            {
                "success": True,
                "deleted_users": deleted_users
            }
        )


class GetShajaraByFamilyTreeAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, month):
        if request.user.is_staff:
            user = get_object_or_404(User, user_id=187070770)
            user_id = user.id
        else:
            user_id = request.user.id
        data = get_shajara_by_family_tree(user_id=user_id, month=month)
        return Response(data)


class GetShajaraByFamilyTreeSelfAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, month, pk):
        if request.user.is_staff:
            user = get_object_or_404(User, user_id=187070770)
            user_id = user.id
        else:
            user = get_object_or_404(User, id=pk)
            user_id = user.id

        data = get_shajara_by_family_tree(user_id=user_id, month=month)
        return Response(data)
