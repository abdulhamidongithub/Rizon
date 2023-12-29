import random

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from users.models import CODE_VERIFIED, DONE
from .models import *
from warehouses.serializers import WarehouseSerializer
from users.serializers import ForAdminUsersSerializer

class EmployeeSerializer(ModelSerializer):
    warehouse = WarehouseSerializer(read_only=True)
    user = ForAdminUsersSerializer(read_only=True)
    class Meta:
        model = Employee
        fields = ("id", "user", "warehouse", "date")


class PostEmployeeSerializer(ModelSerializer):
    # warehouse = WarehouseSerializer(read_only=True)
    class Meta:
        model = Employee
        fields = ("id", "user", "warehouse", "date")

    # def validate_user_id(self, user_id):
    #     a = user_id
    #     if str(a).isdigit() and len(str(a)) > 7:
    #         return user_id
    #     else:
    #         user_id = int("".join([str(random.randint(0, 100) % 10) for _ in range(10)]))
    #         return user_id
    #
    #
    # def validate_username(self, username):
    #     if len(username) < 8 or len(username) > 40:
    #         raise ValidationError({
    #             "success": False,
    #             "message": "Username minimum 8 ta maksimum 40 belgidan iborat bo'lishi mumkin holos !"
    #         })
    #     if username.isdigit():
    #         raise ValidationError({
    #             "success": False,
    #             "message": "Ushbu username faqat sonlardan iborat !"
    #         })
    #
    #     try:
    #         Employee.objects.get(username=username)
    #         raise ValidationError({
    #             "success": False,
    #             "message": "Ushbu username allaqachon mavjud !"
    #         })
    #     except:
    #         pass
    #
    #     return username
    #
    # def validate_password(self, password):
    #     if str(password).isdigit():
    #         raise ValidationError({
    #             "success": False,
    #             "message": "Ushbu parol faqat sonlardan iborat !"
    #         })
    #     return password
    #
    # def validate_passport(self, passport):
    #     if str(passport).isdigit():
    #         raise ValidationError({
    #             "success": False,
    #             "message": "Passport seriyasi ma'lumotlari noto'g'ri kiritilid !"
    #         })
    #     if str(str(passport[:2])).isascii() == False:
    #         raise ValidationError({
    #             "success": False,
    #             "message": "Passport seriyasi noto'g'ri kiritildi !"
    #         })
    #
    #     try:
    #         Employee.objects.get(passport=passport)
    #         raise ValidationError({
    #             "success": False,
    #             "message": "Passport ma'lumotlari noto'g'ri !"
    #         })
    #
    #     except:
    #         return passport
    #
    # def validate_phoneNum(self, phoneNum):
    #     try:
    #         Employee.objects.get(phoneNum=phoneNum)
    #         # raise APIException({
    #         #     "success": False,
    #         #     "message": "Ushbu telefon raqami orqali avval ro'yxatdan o'tilgan !"
    #         # })
    #         raise APIException("Ushbu telefon raqami orqali avval ro'yxatdan o'tilgan !")
    #
    #     except:
    #         return phoneNum


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



class EmployeeSerializer2(ModelSerializer):
    # warehouse = WarehouseSerializer()
    class Meta:
        model = Employee
        fields = ("id", "user", "warehouse", "date")


class EmployeeSalarySerializer(ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = EmployeeSalaryPayments
        fields = "__all__"


class PostEmployeeSalarySerializer(serializers.Serializer):
    employee = serializers.CharField(required=True)
    paid = serializers.IntegerField(required=True)

    # class Meta:
    #     model = EmployeeSalaryPayments
    #     fields = ("employee", "paid")
    #
    # def validate(self, data):
    #     sana = data.get("date")
    #     data["date"] = f"{sana}-10"
    #     return data


def insteadGetEmployeeInfoSerializer(employee, many=False):
    if many==False:
        employee_ser = EmployeeSerializer(employee).data
        # fields = ("id", "user", "warehouse", "date")
        data = employee_ser.pop('user')
        employee_ser.pop("id")
        data.update(employee_ser)

        return data
    else:
        all_data = []
        for emp in employee:
            employee_ser = EmployeeSerializer(emp).data
            data = employee_ser.pop('user')
            employee_ser.pop("id")
            data.update(employee_ser)

            all_data.append(data)

        return all_data

class CreateEmployeeSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    # confirm_password = serializers.CharField(write_only=True, required=True)

    # user_id = serializers.IntegerField(write_only=True, required=True)
    passport = serializers.CharField(write_only=True, required=True)
    address = serializers.CharField(write_only=True, required=True)
    phoneNumTwo = serializers.CharField(write_only=True, required=True)
    dateOfBirth = serializers.DateField(write_only=True, required=True)

    warehouse = serializers.UUIDField(write_only=True, required=True)

    # def validate(self, data):
    #     password = data.get('password', None)
    #     confirm_password = data.get('confirm_password', None)
    #     if password !=confirm_password:
    #         raise ValidationError(
    #             {
    #                 "message": "Parolingiz va tasdiqlash parolingiz bir-biriga teng emas"
    #             }
    #         )
    #     if password:
    #         validate_password(password)
    #         validate_password(confirm_password)
    #
    #     return data

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
        instance.warehouse = validated_data.get('warehouse', instance.warehouse)

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class EmployeeSaleMiniWarehouseSerializer(serializers.Serializer):
    miniwarehouse = serializers.CharField(write_only=True, required=True)
    product = serializers.CharField(write_only=True, required=True)
    amount = serializers.IntegerField(write_only=True, required=True)
