# from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ModelSerializer

# from employees.serializers import EmployeeSerializer2
from products.serializers import ProductSerializer
from users.serializers import UsersSerializer, ForAdminUsersSerializer
from .models import *


class WarehouseSerializer(ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ("id", "name", "address", "phone", "photo", "about")


class WarehouseProductSerializer(ModelSerializer):
    warehouse = WarehouseSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = WarehouseProduct
        fields = "__all__"

class PostWarehouseProductSerializer(ModelSerializer):
    class Meta:
        model = WarehouseProduct
        # fields = ("product", "warehouse", "amount", "paid")
        fields = "__all__"

    # def validate(self, data):
    #     product = get_object_or_404(Product, id=data.get('product'))
    #     product_Ser = ProductSerializer(product).data
    #
    #     # data['summa'] = product_Ser['summa'] * data.get('amount')
    #     data.update({'summa': product_Ser['summa'] * data.get('amount')})
    #
    #     return data

    # def update(self, instance, validated_data):
    #     instance.product = validated_data.get('product', instance.product)
    #     instance.warehouse = validated_data.get('warehouse', instance.warehouse)
    #     instance.amount = validated_data.get('amount', instance.amount)
    #     instance.paid = validated_data.get('paid', instance.paid)
    #     instance.summa = validated_data.get('summa', instance.summa)
    #
    #     # summa = validated_data.pop("summa")
    #     c_product = validated_data.get('product', instance.product)
    #     c_amount = validated_data.get('amount', instance.amount)
    #
    #     product = get_object_or_404(Product, id=c_product)
    #     product_Ser = ProductSerializer(product).data
    #
    #     # summa = product_Ser['price'] * c_amount
    #     summa = 12000000
    #     instance.summa = summa
    #
    #     instance.save()
    #     # return super(PostWarehouseProductSerializer, self).update(instance, validated_data)
    #     return instance


class EmployeeSerializer3(ModelSerializer):
    warehouse = WarehouseSerializer(read_only=True)
    user = ForAdminUsersSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "user", "warehouse", "date")


class WarehouseSaleProductSerializer(ModelSerializer):
    warehouse = WarehouseSerializer(read_only=True)
    employee = EmployeeSerializer3(read_only=True)
    user = UsersSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = WarehouseSaleProduct
        fields = "__all__"


class PostWarehouseSaleProductSerializer2(ModelSerializer):
    class Meta:
        model = WarehouseSaleProduct
        fields = ("amount", "user", "product")


class PostWarehouseSaleProductSerializer3(ModelSerializer):
    class Meta:
        model = WarehouseSaleProduct
        fields = ("amount", "user", "product", "dateTime")


class PostWarehouseSaleProductSerializer(ModelSerializer):
    class Meta:
        model = WarehouseSaleProduct
        fields = "__all__"

def insteadGetEmployeeInfoSerializer2(employee, many=False):
    if many==False:
        employee_ser = EmployeeSerializer3(employee).data
        # fields = ("id", "user", "warehouse", "date")
        data = employee_ser['user']
        data['warehouse'] = employee_ser['warehouse']
        data['date'] = employee_ser['date']
        data['id'] = employee_ser['id']

        return data
    else:
        all_data = []
        for emp in employee:
            employee_ser = EmployeeSerializer3(emp).data
            data = employee_ser['user']
            data['warehouse'] = employee_ser['warehouse']
            data['date'] = employee_ser['date']
            data['id'] = employee_ser['id']

            all_data.append(data)

        return all_data

