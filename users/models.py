import random
import uuid
from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel

ORDINARY_USER, MANAGER, ADMIN, EMPLOYEE, MEDIC, BRAND_MANAGER = ("ordinary_user", 'manager', 'admin', "employee", "medic", "brand_manager")
VIA_EMAIL, VIA_PHONE = ("via_email", "via_phone")
NEW, CODE_VERIFIED, DONE, PHOTO_DONE = ('new', 'code_verified', 'done', 'photo_done')
CASHBACK, VOUCHER, TRAVEL, UMRAH, AUTOBONUS = ('Cashback', 'Voucher', 'Travel', 'Umra', 'Avtobonus')


class User(AbstractUser, BaseModel):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN),
        (EMPLOYEE, EMPLOYEE),
        (MEDIC, MEDIC),
        (BRAND_MANAGER, BRAND_MANAGER)
    )
    AUTH_TYPE_CHOICES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE)
    )

    user_roles = models.CharField(max_length=31, choices=USER_ROLES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPE_CHOICES)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic', 'heif'])])

    user_id = models.BigIntegerField(unique=True, null=True)
    passport = models.CharField(max_length=15, unique=True, null=True)
    address = models.CharField(max_length=255, null=True)
    phoneNumTwo = models.CharField(max_length=20, null=True)
    dateOfBirth = models.DateField(null=True)
    date = models.DateTimeField(auto_created=True, auto_now_add=True)
    # date = models.DateTimeField()
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 10000) % 10) for _ in range(6)])
        # code = "150150"
        UserConfirmation.objects.create(
            user_id=self.id,
            verify_type=verify_type,
            code=code
        )
        return code

    def create_user_tree(self, teacher_id):
        UsersTree.objects.create(
            offerer_id = teacher_id,
            invited_id = self.id
        )
        return True

    def create_user_id_for_user(self):
        if not self.user_id:
            new_user_id = int("".join([str(random.randint(0, 10000) % 10) for _ in range(10)]))
            while User.objects.filter(user_id=new_user_id):
                new_user_id = new_user_id + random.randint(1, 10000)
            self.user_id = new_user_id


    def check_username(self):
        if not self.username:
            temp_username = f'rizon-{uuid.uuid4().__str__().split("-")[-1]}' # instagram-23324fsdf
            while User.objects.filter(username=temp_username):
                temp_username = f"{temp_username}{random.randint(0,9)}"
            self.username = temp_username

    def check_email(self):
        if self.email:
            normalize_email = self.email.lower()  # aKhamdjon@gmail.com -> akhamdjon@gmail.com
            self.email = normalize_email

    def check_pass(self):
        if not self.password:
            temp_password = f'password-{uuid.uuid4().__str__().split("-")[-1]}' #  123456mfdsjfkd
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }

    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)

    def clean(self):
        self.check_email()
        self.check_username()
        self.check_pass()
        self.hashing_password()

PHONE_EXPIRE = 2
EMAIL_EXPIRE = 5


class UserConfirmation(BaseModel):
    TYPE_CHOICES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )
    code = models.CharField(max_length=6)
    verify_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    user = models.ForeignKey('users.User', models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:  # 30-mart 11-33 + 5minutes
            self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
        else:
            self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)


########################################################################################################################\

class UsersTree(BaseModel):
    offerer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offerer")  # teacher
    invited = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invited")  # follower
    date = models.DateTimeField(auto_created=True, auto_now_add=True, null=True)
    deleted = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f"{self.offerer} {self.invited}"



class UsersSalaryPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paid = models.BigIntegerField()
    salary_payer = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    paymentDate = models.DateTimeField(auto_created=True, auto_now_add=True, null=True)
    # paymentDate = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.user} {self.paid} {self.date} {self.paymentDate}"


class UsersCoupon(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    used = models.BigIntegerField()
    comment = models.TextField(null=True)
    dateTime = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.used} {self.dateTime}"


class CouponTransfer(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_user")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_user")
    used = models.BigIntegerField(validators=[MinValueValidator(1000)])
    comment = models.TextField(null=True)
    dateTime = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return f"{self.sender} {self.used} {self.dateTime}"


class Notification(BaseModel):
    title = models.CharField(max_length=255)
    message = models.TextField()
    date = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self): return self.title

class UserNotification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField(null=True)
    date = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self): return f"{self.title}"


class OurTeam(BaseModel):
    full_name = models.CharField(max_length=255)
    job = models.CharField(max_length=255)
    about = models.TextField(null=True)
    photo = models.FileField(blank=True, upload_to="team")

    def __str__(self): return f"{self.full_name}"


class UserSalary(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.CASCADE)
    user_status = models.CharField(max_length=255)
    user_score = models.BigIntegerField()
    user_tree_score = models.BigIntegerField()
    user_tree_summa = models.BigIntegerField()
    personal_bonus = models.BigIntegerField()
    extra_bonus = models.BigIntegerField()
    coupon = models.BigIntegerField()
    forMentorship = models.BigIntegerField()
    bonus_for_followers_status = models.BigIntegerField()
    collective_bonus_amount = models.BigIntegerField()
    stat_percent = models.BigIntegerField()
    for_followers_status_percent = models.BigIntegerField()
    salary = models.BigIntegerField()
    paid = models.BigIntegerField()
    debt = models.BigIntegerField()
    month = models.DateField()

    def __str__(self):
        return f"{self.user}"


class BonusAccount(BaseModel):
    BONUS_TYPES = (
        (CASHBACK, CASHBACK),
        (VOUCHER, VOUCHER),
        (TRAVEL, TRAVEL),
        (UMRAH, UMRAH),
        (AUTOBONUS, AUTOBONUS)
    )
    bonus_type = models.CharField(max_length=50, choices=BONUS_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bonus_account")
    status = models.CharField(max_length=50)
    amount = models.BigIntegerField()
    month = models.CharField(max_length=50)
    comment = models.CharField(max_length=1000)
    payer = models.ForeignKey("warehouses.Warehouse", on_delete=models.CASCADE, related_name="payer", null=True)

    def __str__(self): return self.user.__str__()
