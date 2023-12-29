from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from products.serializers import ProductSerializer
from users.serializers import ForAdminUsersSerializer
from .models import *


# class PostMedProductSerializer2(serializers.Serializer):
#     medic = serializers.CharField(write_only=True, required=True)
#     product = serializers.CharField(write_only=True, required=True)
#
#     # class Meta:
#     #     model = MedProduct

class PostMedProductSerializer2(ModelSerializer):
    # medic = serializers.CharField(write_only=True, required=True)
    # product = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = MedProduct
        fields = "__all__"


class MedicSerializer(ModelSerializer):
    user = ForAdminUsersSerializer(read_only=True)
    class Meta:
        model = Medic
        fields = ("id", "user", "degree", "university", "bio", "date", "share_of_sales_percent")

    # def create(self, validated_data):
    #     password = validated_data.pop('password', None)
    #     instance = self.Meta.model(**validated_data)
    #
    #     # Adding the below line made it work for me.
    #     instance.is_active = True
    #     if password is not None:
    #         # Set password does the hash, so you don't need to call make_password
    #         instance.set_password(password)
    #     instance.save()
    #     return instance


class MedProductSerializer(ModelSerializer):
    medic = MedicSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    class Meta:
        model = MedProduct
        fields = "__all__"

class ForOthersMedProductSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = MedProduct
        fields = "__all__"


class PostMedProductSerializer(ModelSerializer):
    class Meta:
        model = MedProduct
        fields = "__all__"


class MedSalarySerializer(ModelSerializer):
    medic = MedicSerializer(read_only=True)
    class Meta:
        model = MedSalaryPayment
        fields = "__all__"


class PostMedSalarySerializer(ModelSerializer):
    class Meta:
        model = MedSalaryPayment
        fields = ("medic", "paid")

    def validate(self, data):
        sana = data.get("date")
        data["date"] = f"{sana}-10"
        return data



def insteadGetMeddicInfoSerializer(medic, many=False):
    if many==False:
        medic_ser = MedicSerializer(medic).data
        data = medic_ser.pop('user')
        # medic_ser.pop("id")
        data.update(medic_ser)

        return data
    else:
        all_data = []
        for med in medic:
            medic_ser = MedicSerializer(med).data
            data = medic_ser.pop('user')
            # medic_ser.pop("id")
            data.update(medic_ser)

            all_data.append(data)

        return all_data