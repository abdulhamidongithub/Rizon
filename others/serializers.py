from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from users.serializers import ForOthersUsersSerializer
from .models import *


class PromotionSerializer(ModelSerializer):
    class Meta:
        model = Promotion
        fields = ("id", "name", "coupon", "pause", "photo")


class PutPromotionSerializer(ModelSerializer):
    class Meta:
        model = Promotion
        fields = ("pause",)


class PromotionAmountSerializer(ModelSerializer):
    class Meta:
        model = PromotionAmount
        fields = "__all__"



class SalePromotionSerializer(ModelSerializer):
    promotion = PromotionSerializer(read_only=True)
    user = ForOthersUsersSerializer(read_only=True)
    class Meta:
        model = SalePromotion
        fields = "__all__"


class PostSalePromotionSerializer(ModelSerializer):
    class Meta:
        model = SalePromotion
        fields = ("promotion", "amount")


class ActivateArchiveInfosSerializer(serializers.Serializer):
    deleted = serializers.BooleanField(required=True)


class ForUpdateUsersRolesSerializer(serializers.Serializer):
    user_role = serializers.CharField(required=True)


class ChangeUserTreeSerializer(serializers.Serializer):
    offerer = serializers.IntegerField(required=True)
    invited = serializers.IntegerField(required=True)


class TransferBonusAccountSerializer(serializers.Serializer):
    user = serializers.CharField(required=True)
    from_bonus_type = serializers.CharField(required=True)
    to_bonus_type = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)


class UseBonusAccountSerializer(serializers.Serializer):
    user = serializers.CharField(required=True)
    bonus_type = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)


class BaseParametrSerializer(ModelSerializer):
    class Meta:
        model = BaseParametr
        fields = (
            "bonus_account_lifetime_month",
            "bonus_account_lifetime_month_break"
        )
