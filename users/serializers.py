from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from shared.utility import check_email_or_phone, send_phone_code, check_user_type
from .models import User, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_DONE, OurTeam, \
    CouponTransfer, Notification, UsersTree, UsersCoupon, UsersSalaryPayment, UserNotification, BRAND_MANAGER, \
    MANAGER, BonusAccount
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status'
        )
        extra_kwargs = {
            'auth_type': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False}
        }

    def create(self, validated_data):
        validated_data['date'] = datetime.today()
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            # send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_phone_code(user.phone_number, code)
        user.create_user_id_for_user()
        user.save()
        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)  # email or phone
        if input_type == "email":
            data = {
                "email": user_input,
                "auth_type": VIA_EMAIL
            }
        elif input_type == "phone":
            data = {
                "phone_number": user_input,
                "auth_type": VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': "You must send email or phone number"
            }
            raise ValidationError(data)

        return data

    def validate_email_phone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                "success": False,
                "message": "Bu email allaqachon ma'lumotlar bazasida bor"
            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                "success": False,
                "message": "Bu telefon raqami allaqachon ma'lumotlar bazasida bor"
            }
            raise ValidationError(data)

        return value

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data


class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    user_id = serializers.IntegerField(write_only=True, required=True)
    passport = serializers.CharField(write_only=True, required=True)
    address = serializers.CharField(write_only=True, required=True)
    phoneNumTwo = serializers.CharField(write_only=True, required=True)
    dateOfBirth = serializers.DateField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError(
                {
                    "message": "Parolingiz va tasdiqlash parolingiz bir-biriga teng emas"
                }
            )
        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data

    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            raise ValidationError(
                {
                    "message": "Username must be between 5 and 30 characters long"
                }
            )
        if username.isdigit():
            raise ValidationError(
                {
                    "message": "This username is entirely numeric"
                }
            )
        return username

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        instance.username = validated_data.get('username', instance.username)
        instance.passport = validated_data.get('passport', instance.passport)
        instance.address = validated_data.get('address', instance.address)
        instance.phoneNumTwo = validated_data.get('phoneNumTwo', instance.phoneNumTwo)
        instance.dateOfBirth = validated_data.get('dateOfBirth', instance.dateOfBirth)
        instance.user_id = validated_data.get('user_id', instance.user_id)

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic', 'heif'])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def auth_validate(self, data):
        user_input = data.get('userinput')  # email, phone_number, username
        if check_user_type(user_input) == 'username':
            username = user_input
        elif check_user_type(user_input) == "email":  # Anora@gmail.com   -> anOra@gmail.com
            user = self.get_user(email__iexact=user_input)  # user get method orqali user o'zgartiruvchiga biriktirildi
            username = user.username
        elif check_user_type(user_input) == 'phone':
            user = self.get_user(phone_number=user_input)
            username = user.username
        else:
            data = {
                'success': True,
                'message': "Siz email, username yoki telefon raqami jo'natishingiz kerak"
            }
            raise ValidationError(data)

        authentication_kwargs = {
            self.username_field: username,
            'password': data['password']
        }
        # user statusi tekshirilishi kerak
        current_user = User.objects.filter(username__iexact=username).first()  # None

        if current_user is not None and current_user.auth_status in [NEW, CODE_VERIFIED]:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Siz ro'yxatdan to'liq o'tmagansiz!"
                }
            )
        user = authenticate(**authentication_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Sorry, login or password you entered is incorrect. Please check and trg again!"
                }
            )

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_DONE]:
            raise PermissionDenied("Siz login qila olmaysiz. Ruxsatingiz yoq")
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        data['full_name'] = self.user.full_name
        if self.user.user_roles == BRAND_MANAGER:
            data['user_role'] = MANAGER
        else:
            data['user_role'] = self.user.user_roles
        return data

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError(
                {
                    "message": "No active account found"
                }
            )
        return users.first()


class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone', None)
        if email_or_phone is None:
            raise ValidationError(
                {
                    "success": False,
                    'message': "Email yoki telefon raqami kiritilishi shart!"
                }
            )
        user = User.objects.filter(Q(phone_number=email_or_phone) | Q(email=email_or_phone))
        if not user.exists():
            raise NotFound(detail="User not found")
        attrs['user'] = user.first()
        return attrs


class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    confirm_password = serializers.CharField(min_length=8, required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'confirm_password'
        )

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('password', None)
        if password != confirm_password:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Parollaringiz qiymati bir-biriga teng emas"
                }
            )
        if password:
            validate_password(password)
        return data

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        return super(ResetPasswordSerializer, self).update(instance, validated_data)

###############################################################################################


class UsersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "first_name", "last_name", "user_id", "passport", "address", "phone_number", "phoneNumTwo", "dateOfBirth", "date", "photo", 'email')

    def validate_username(self, username):
        if len(username) < 8 or len(username) > 40:
            raise ValidationError({
                "success": False,
                "message": "Username minimum 8 ta maksimum 40 belgidan iborat bo'lishi mumkin holos !"
            })

        if username.isdigit():
            raise ValidationError({
                "success": False,
                "message": "Ushbu username faqat sonlardan iborat !"
            })
        try:
            User.objects.get(username=username)
            raise ValidationError({
                "success": False,
                "message": "Ushbu username allaqachon mavjud !"
            })
        except:
            pass
        return username

    def validate_password(self, password):
        if str(password).isdigit():
            raise ValidationError({
                "success": False,
                "message": "Ushbu parol faqat sonlardan iborat !"
            })
        return password

    def validate_passport(self, passport):
        try:
            User.objects.get(passport=passport)
            raise ValidationError({
                "success": False,
                "message": "Passport ma'lumotlari noto'g'ri !"})

        except:
            return passport

    def validate_phoneNum(self, phoneNum):
        try:
            User.objects.get(phoneNum=phoneNum)
            raise ValidationError({
                "success": False,
                "message": "Ushbu telefon raqami orqali avval ro'yxatdan o'tilgan !"
            })

        except:
            return phoneNum

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        # Adding the below line made it work for me.
        instance.is_active = True
        if password is not None:
            # Set password does the hash, so you don't need to call make_password
            instance.set_password(password)
        instance.save()
        return instance


class ForOthersUsersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "user_id", "phoneNumTwo", "phone_number", "date", "photo", "email", "passport", "address", "dateOfBirth")


class ForAdminUsersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "user_id", "username", "phoneNumTwo", "phone_number", "date", "photo", "passport", "address", "dateOfBirth", "date")


class UsersSalarySerializer(ModelSerializer):
    user = ForOthersUsersSerializer(read_only=True)
    class Meta:
        model = UsersSalaryPayment
        fields = "__all__"


class PostUsersSalarySerializer(ModelSerializer):
    class Meta:
        model = UsersSalaryPayment
        fields = "__all__"


class PostUsersSalarySerializer2(ModelSerializer):
    class Meta:
        model = UsersSalaryPayment
        fields = ("user", "paid")

    def validate(self, data):
        sana = data.get("date")
        data["date"] = f"{sana}-10"
        return data


class UsersCouponSerializer(ModelSerializer):
    user = ForOthersUsersSerializer(read_only=True)
    class Meta:
        model = UsersCoupon
        fields = "__all__"


class PostUsersCouponSerializer(ModelSerializer):
    class Meta:
        model = UsersCoupon
        fields = "__all__"


class UsersTreeSerializer(ModelSerializer):
    invited = ForOthersUsersSerializer(read_only=True)
    offerer = ForOthersUsersSerializer(read_only=True)
    class Meta:
        model = UsersTree
        fields = "__all__"


class PostUsersTreeSerializer(ModelSerializer):
    class Meta:
        model = UsersTree
        fields = "__all__"


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class UserNotificationSerializers(ModelSerializer):
    class Meta:
        model = UserNotification
        fields = "__all__"


class CouponTransferSerializer(ModelSerializer):
    sender = ForOthersUsersSerializer(read_only=True)
    receiver = ForOthersUsersSerializer(read_only=True)

    class Meta:
        model = CouponTransfer
        fields = "__all__"


class PostCouponTransferSerializer(ModelSerializer):
    class Meta:
        model = CouponTransfer
        fields = ("used", "receiver", "comment")


class OurTeamSerializer(ModelSerializer):
    class Meta:
        model = OurTeam
        fields = "__all__"


class BonusAccountSerializer(ModelSerializer):
    class Meta:
        model = BonusAccount
        # fields = "__all__"
        fields = (
            "bonus_type",
            "status",
            "amount",
            "month",
            "comment"
        )


class AdminBonusAccountSerializer(ModelSerializer):
    first_name = serializers.SerializerMethodField("get_first_name")
    last_name = serializers.SerializerMethodField("get_last_name")
    user_id = serializers.SerializerMethodField("get_user_id")

    class Meta:
        model = BonusAccount
        # fields = "__all__"
        fields = (
            "first_name",
            "last_name",
            "user_id",
            "bonus_type",
            "status",
            "amount",
            "month",
            "comment"
        )

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_user_id(self, obj):
        return obj.user.user_id
