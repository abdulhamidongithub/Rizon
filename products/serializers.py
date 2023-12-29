from django.core.validators import FileExtensionValidator
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from users.serializers import ForOthersUsersSerializer

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "extraPrice", "about", "photo_link", "date", "manufacturer", "expiration_date", "product_type")


class ProductSerializer2(serializers.Serializer):
    name = serializers.CharField(write_only=True, required=True)
    about = serializers.CharField(write_only=True, required=True)
    # photo_link = serializers.FileField(write_only=True, required=True)
    photo_link = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic', 'heif'])])
    manufacturer = serializers.CharField(write_only=True, required=True)
    expiration_date = serializers.CharField(write_only=True, required=True)
    product_type = serializers.CharField(write_only=True, required=True)
    price = serializers.IntegerField(write_only=True, required=True)
    extraPrice = serializers.IntegerField(write_only=True, required=True)

    # class Meta:
    #     model = Product
    #     fields = ("id", "name", "price", "extraPrice", "about", "photo_link", "manufacturer", "expiration_date", "product_type")


class ProductSerializer22(ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "extraPrice", "about", "photo_link", "date", "manufacturer", "expiration_date", "product_type", "discount")


class ProductOrderSerializer(ModelSerializer):
    product = ProductSerializer()
    user = ForOthersUsersSerializer()
    class Meta:
        model = ProductOrder
        # fields = ("id", "product", "user", "amount", "date", "done", "warehouse")
        fields = "__all__"


class PostProductOrderSerializer(ModelSerializer):
    class Meta:
        model = ProductOrder
        fields = ("product", "amount", "warehouse")
        # fields = "__all__"


class PostProductDiscountSerializer(ModelSerializer):
    class Meta:
        model = Product
        # fields = ("id", "product", "user", "amount", "date", "done", "warehouse")
        fields = ("discount")



class LandingProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "extraPrice", "about", "photo_link", "manufacturer", "expiration_date", "product_type", "rate")


class LandingProductSerializer2(ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "extraPrice", "about", "photo_link", "manufacturer", "expiration_date", "product_type", "discount", "rate")


class ProductCommentSerializer(ModelSerializer):
    product = LandingProductSerializer(read_only=True)
    class Meta:
        model = ProductComment
        fields = "__all__"


class ProductDiscountSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = ProductDiscount
        fields = "__all__"

class ProductDiscountSerializerForLanding(ModelSerializer):
    product = LandingProductSerializer2(read_only=True)
    class Meta:
        model = ProductDiscount
        fields = "__all__"


class PostProductDiscountSerializer2(ModelSerializer):
    class Meta:
        model = ProductDiscount
        fields = "__all__"


class LandingProductOrderSerializer(ModelSerializer):
    class Meta:
        model = LandingProductOrder
        # fields = "__all__"
        fields = ("customer", "product", "warehouse", "amount")


def forLandiingPoductSerializer(products, many=False):
    if many==False:
        product = ProductDiscountSerializerForLanding(products).data
        data = product.pop('product')
        data.update(product)

        return data
    else:
        all_data = []
        for product in products:
            product_ser = ProductDiscountSerializerForLanding(product).data
            data = product_ser.pop('product')
            data.update(product_ser)

            all_data.append(data)
        return all_data