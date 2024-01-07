import datetime

from django.db.models import Sum
from django.shortcuts import render
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.employee_per import IsEmployee
from employees.models import EmployeeSalaryPayments
from employees.serializers import EmployeeSalarySerializer
from others.rv_ball import rv_ball
from products.models import ProductDiscount
from products.serializers import forLandiingPoductSerializer
from users.models import UsersSalaryPayment
from users.serializers import UsersSalarySerializer
from .models import *
from .serializers import *


class WarehoueseTransferSaleData(APIView):
    def post(self, request):
        try:
            sale = WarehouseSaleProduct.objects.create(
                warehouse=Warehouse.objects.get(phone=request.data.get("warehouse")),
                employee=Employee.objects.get(user__username=request.data.get("employee")),
                user=User.objects.get(username=request.data.get("user")),
                product=Product.objects.get(name=request.data.get("product")),
                amount=request.data.get("amount"),
                summa=request.data.get("summa"),
                dateTime=request.data.get("dateTime")
            )
            sale_ser = WarehouseSaleProductSerializer(sale).data
            return Response(sale_ser)
        except:
            return Response({
                "success": False,
                "dateTime": f"{request.data.get('dateTime')}",
                "message": "#################################################################################################################\n" +
                           "##################################################################################################################\n" +
                           "###################################################################################################################\n" +
                           "###################################################################################################################\n" +
                           "###################################################################################################################\n" +
                           "##########################################################"
            })



class WarehouseSaleProductTransferData(APIView):
    def post(self, request):
        warehouse = Warehouse.objects.get(id=request.data.get("warehouse"))
        employee = Employee.objects.get(id=request.data.get("employee"))
        user = User.objects.get(id=request.data.get("user"))
        product = Product.objects.get(id=request.data.get("product"))
        sale = WarehouseSaleProduct.objects.create(
            warehouse = warehouse,
            employee = employee,
            user = user,
            product = product,
            amount = request.data.get("amount"),
            summa = request.data.get("summa"),
            dateTime = request.data.get("dateTime")
        )
        sale_Ser = WarehouseSaleProductSerializer(sale).data
        return Response(sale_Ser)

class WarehouseProductTransferData(APIView):
    def post(self, request):
        warehouse = Warehouse.objects.get(phone=request.data.get("warehouse"))
        product = Product.objects.get(name=request.data.get("product"))
        sale = WarehouseProduct.objects.create(
            warehouse = warehouse,
            product = product,
            amount = request.data.get("amount"),
            summa = request.data.get("summa"),
            dateTime = request.data.get("dateTime")
        )
        sale_Ser = WarehouseProductSerializer(sale).data
        return Response(sale_Ser)


# Warehouse
class WarehouseListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = Warehouse.objects.filter(deleted=False)
    serializer_class = WarehouseSerializer

    def create(self, request, *args, **kwargs):
        if request.user.is_staff:
            ser = WarehouseSerializer(data=request.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)
            else:
                return Response(ser.errors)
        else:
            return ValidationError({
                "message": "You do not have permission to perform this action."
            })

class WarehouseGetEmployees(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Warehouse.objects.filter(deleted=False)
    serializer_class = WarehouseSerializer

    def get(self, request, *args, **kwargs):
        warehouse = Warehouse.objects.get(id=kwargs['pk'])
        warehouse_ser = WarehouseSerializer(warehouse).data
        employees = Employee.objects.filter(warehouse__id=kwargs['pk'])
        employees_ser = insteadGetEmployeeInfoSerializer2(employees, many=True)

        return Response({"warehouse": warehouse_ser, "employees": employees_ser})


class WarehouseGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Warehouse.objects.filter(deleted=False)
    serializer_class = WarehouseSerializer

    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            Warehouse.objects.filter(id=kwargs["pk"]).update(deleted=True)
            return Response({"detail": "deleted"})
        else:
            return Response({"detail": "You cannot perform this action"})




# WarehouseProduct
class WarehouseProductListCreate(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = WarehouseProduct.objects.all()
    serializer_class = WarehouseProductSerializer


    # def create(self, request, *args, **kwargs):
    #     ser = PostWarehouseProductSerializer(data=request.data)
    #     if ser.is_valid():
    #         # warehouse = get_object_or_404(Warehouse, id=ser.data.get("warehouse"))
    #         # product = get_object_or_404(Product, id=ser.data.get("product"))
    #
    #         # WarehouseProduct.objects.create(
    #         #     warehouse = warehouse,
    #         #     product = product,
    #         #     paid = ser.data.get("paid"),
    #         #     summa = 120000000,
    #         #     amount = ser.data.get("amount")
    #         # )
    #         # ser.save()
    #         return Response(ser.data)
    #     else:
    #         return Response(ser.errors)


class WarehouseGetProducts(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = WarehouseProduct.objects.all()
    serializer_class = WarehouseProductSerializer

    def get(self, request, *args, **kwargs):
        warehouse = Warehouse.objects.get(id=kwargs['pk'])
        warehouse_ser = WarehouseSerializer(warehouse)
        warehouse_products = WarehouseProduct.objects.filter(warehouse__id=kwargs['pk'])
        warehouse_products_ser = WarehouseProductSerializer(warehouse_products, many=True)

        products_Data = {}
        for i in warehouse_products_ser.data:
            product = i['product']

            if product['name'] not in products_Data.keys():
                product_sum = WarehouseProduct.objects.filter(warehouse__id=kwargs['pk'], product__id=product['id']).aggregate(Sum('amount'))
                sale_product = WarehouseSaleProduct.objects.filter(warehouse__id=kwargs['pk'], product__id=product['id']).aggregate(Sum('amount'))

                if sale_product['amount__sum'] is not None:
                    products_Data[product['name']] = {"amount": product_sum['amount__sum'] - sale_product['amount__sum'], "price": product['price']}
                else:
                    products_Data[product['name']] = {"amount": product_sum['amount__sum'], "price": product['price']}

        return Response({"warehouse": warehouse_ser.data, "warehouse_products": products_Data})



class WarehouseProductGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = WarehouseProduct.objects.all()
    serializer_class = WarehouseProductSerializer



class WarehouseList(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = Warehouse.objects.filter(deleted=False, warehouse_type=MINIWAREHOUSE)
    serializer_class = WarehouseSerializer



# WarehouseSaleProduct
class WarehouseSaleProductsGetDataByMonth(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = WarehouseSaleProduct.objects.all()
    serializer_class = WarehouseSaleProductSerializer

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        products_ser = ProductSerializer(products, many=True)

        sales_data = []
        for product in products_ser.data:
            product_sales_sum = WarehouseSaleProduct.objects.filter(product__id=product['id'], dateTime__startswith=str(kwargs['date'])[:7]).aggregate(Sum('summa'))
            product_sales_amount = WarehouseSaleProduct.objects.filter(product__id=product['id'], dateTime__startswith=str(kwargs['date'])[:7]).aggregate(Sum('amount'))
            if product_sales_sum['summa__sum'] is not None:
                sales_data.append({"product": product, "summa": product_sales_sum['summa__sum'], "amount": product_sales_amount['amount__sum'] if product_sales_amount['amount__sum'] is not None else 0})
            else:
                sales_data.append({"product": product, "summa": 0, "amount": product_sales_amount['amount__sum'] if product_sales_amount['amount__sum'] is not None else 0})

        return Response({"sales_data": sales_data})



class WarehouseSaleProductListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsEmployee]
    queryset = WarehouseSaleProduct.objects.all()
    serializer_class = WarehouseSaleProductSerializer

    def create(self, request, *args, **kwargs):
        # if IsEmployee:
        #     data_ser = PostWarehouseSaleProductSerializer(data=request.data)
        #     if data_ser.is_valid():
                # if data_ser.data.get('warehouse') == 4:
                #     ser = PostWarehouseSaleProductSerializer(data=request.data)
                #     if ser.is_valid():
                #         ser.save()
                #         return Response({"sale_info": ser.data})
                #     else:
                #         return Response({"productAmount": ser.errors})
                # else:
                #     product_amount = WarehouseProduct.objects.filter(warehouse__id=data_ser.data.get('warehouse'), product__id=data_ser.data.get('product')).aggregate(Sum('amount'))
                #     amount = data_ser.data.get("amount")
                #     sale_products_amount = WarehouseSaleProduct.objects.filter(warehouse__id=data_ser.data.get('warehouse'), product__id=data_ser.data.get('product')).aggregate(Sum('amount'))
                #
                #     if product_amount['amount__sum'] is not None:
                #         if sale_products_amount['amount__sum'] is not None:
                #             if product_amount['amount__sum'] >= int(amount) + sale_products_amount['amount__sum']:
                #                 data_ser.save()
                #                 return Response({"sale_info": data_ser.data})
                #             return Response({"productAmount": product_amount['amount__sum']})
                #         else:
                #             data_ser.save()
                #             return Response({"sale_info": data_ser.data})
                #     else:
                #         return Response({"productAmount": product_amount['amount__sum']})


                # if sale_products_amount['amount__sum'] is not None:
                #     if product_amount['amount__sum'] >= int(amount) + sale_products_amount['amount__sum']:
                #         data_ser.save()
                #         return Response({data_ser.data})
                #     return Response({"productAmount": product_amount['amount__sum']})
                # else:
                #     if product_amount['amount__sum'] >= int(amount):
                #         data_ser.save()
                #         return Response({data_ser.data})
                #     return Response({"productAmount": product_amount['amount__sum']})

            # return Response({data_ser.errors})
        # return Response({"detail": "error"})
            ser = PostWarehouseSaleProductSerializer2(data=request.data)
            if ser.is_valid():
                employee = get_object_or_404(Employee, user=request.user)
                product =get_object_or_404(Product, id=ser.data.get("product"))
                product_ser = ProductSerializer(product).data

                warehouse_products = WarehouseProduct.objects.filter(warehouse=employee.warehouse, product=product).aggregate(Sum('amount'))
                warehouse_products_amount = warehouse_products['amount__sum'] if warehouse_products['amount__sum'] is not None else 0
                sold_products = WarehouseSaleProduct.objects.filter(warehouse=employee.warehouse, product=product).aggregate(Sum('amount'))
                sold_products_amount = sold_products['amount__sum'] if sold_products['amount__sum'] is not None else 0

                discounts = ProductDiscount.objects.filter(product=product, endDate__gte=datetime.datetime.today(), startDate__lte=datetime.datetime.today())
                discount_ser = forLandiingPoductSerializer(discounts, many=True)

                if discount_ser != []:
                    discount_amount = discount_ser[0]["amount"]
                    discount_discount = discount_ser[0]["discount"]
                    s_amount = ser.data.get("amount") // discount_amount * discount_discount
                else:
                    s_amount = ser.data.get("amount")


                if warehouse_products_amount - sold_products_amount - int(ser.data.get("amount")) >= 0:
                    sold = WarehouseSaleProduct.objects.create(
                        warehouse = employee.warehouse,
                        employee = employee,
                        user = get_object_or_404(User, id=ser.data.get("user")),
                        product = product,
                        amount = s_amount,
                        summa = int(ser.data.get("amount")) * product_ser.get("price"),
                        dateTime = datetime.datetime.today()
                    )
                    sold_ser = WarehouseSaleProductSerializer(sold).data
                    # ser.save()
                    return Response({
                        "success": True,
                        "sale_info": sold_ser
                    })
                else:
                    return Response({
                        "success": False,
                        "message": "Sizning filial omboringizda ushbu mahsulotdan qolmagan !"
                    })
            else:
                return Response({"detail": ser.errors})


class WarehouseSaleProductListCreateForFRBot(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsEmployee]
    queryset = WarehouseSaleProduct.objects.all()
    serializer_class = WarehouseSaleProductSerializer

    def create(self, request, *args, **kwargs):
            ser = PostWarehouseSaleProductSerializer3(data=request.data)
            if ser.is_valid():
                employee = get_object_or_404(Employee, user=request.user)
                product =get_object_or_404(Product, id=ser.data.get("product"))
                product_ser = ProductSerializer(product).data

                warehouse_products = WarehouseProduct.objects.filter(warehouse=employee.warehouse, product=product).aggregate(Sum('amount'))
                warehouse_products_amount = warehouse_products['amount__sum'] if warehouse_products['amount__sum'] is not None else 0
                sold_products = WarehouseSaleProduct.objects.filter(warehouse=employee.warehouse, product=product).aggregate(Sum('amount'))
                sold_products_amount = sold_products['amount__sum'] if sold_products['amount__sum'] is not None else 0

                discounts = ProductDiscount.objects.filter(product=product, endDate__gte=datetime.datetime.today(), startDate__lte=datetime.datetime.today())
                discount_ser = forLandiingPoductSerializer(discounts, many=True)

                if discount_ser != []:
                    discount_amount = discount_ser[0]["amount"]
                    discount_discount = discount_ser[0]["discount"]
                    s_amount = ser.data.get("amount") // discount_amount * discount_discount
                else:
                    s_amount = ser.data.get("amount")


                if warehouse_products_amount - sold_products_amount - int(ser.data.get("amount")) >= 0:
                    sold = WarehouseSaleProduct.objects.create(
                        warehouse = employee.warehouse,
                        employee = employee,
                        user = get_object_or_404(User, id=ser.data.get("user")),
                        product = product,
                        amount = s_amount,
                        summa = int(ser.data.get("amount")) * product_ser.get("price"),
                        dateTime = ser.data.get("dateTime")
                    )
                    sold_ser = WarehouseSaleProductSerializer(sold).data
                    # ser.save()
                    return Response({
                        "success": True,
                        "sale_info": sold_ser
                    })
                else:
                    return Response({
                        "success": False,
                        "message": "Sizning filial omboringizda ushbu mahsulotdan qolmagan !"
                    })
            else:
                return Response({"detail": ser.errors})


class WarehouseProductsSaleByMonthToMonth(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request):
        from datetime import datetime
        # import pandas as pd

        # months = pd.period_range("2022-10", str(datetime.today())[:7], freq='M')[::-1][1:]
        months = [str(datetime.today())[:7]]
        warehouses = Warehouse.objects.all()
        products = Product.objects.all()

        sold_data = []

        for month in months:
            data = {
                "month": str(month),
                "warehouses": [str(warehouse.name) for warehouse in warehouses],
                "data": []
            }

            for product in products:
                sold_d = []
                for warehouse in warehouses:
                    sold = WarehouseSaleProduct.objects.filter(warehouse=warehouse, product=product, dateTime__startswith=str(month)).aggregate(Sum('amount'))
                    sold_sum = sold['amount__sum'] if sold['amount__sum'] is not None else 0

                    sold_d.append(sold_sum)
                data['data'].append(
                    {
                        "product": product.name,
                        "data": sold_d
                    }
                )
            sold_data.append(data)

        return Response(sold_data)


class WarehouseProductsSendByMonthToMonth(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)


    def get(self, request):
        from datetime import datetime
        # import pandas as pd

        # months = pd.period_range("2022-10", str(datetime.today())[:7], freq='M')[::-1][1:]
        months = [str(datetime.today())[:7]]
        warehouses = Warehouse.objects.all()
        products = Product.objects.all()

        sold_data = []

        for month in months:
            data = {
                "month": str(month),
                "warehouses": [str(warehouse.name) for warehouse in warehouses],
                "data": []
            }

            for product in products:
                sold_d = []
                for warehouse in warehouses:
                    sold = WarehouseProduct.objects.filter(warehouse=warehouse, product=product, dateTime__startswith=str(month)).aggregate(Sum('amount'))
                    sold_sum = sold['amount__sum'] if sold['amount__sum'] is not None else 0

                    sold_d.append(sold_sum)
                data['data'].append(
                    {
                        "product": product.name,
                        "data": sold_d
                    }
                )
            sold_data.append(data)

        return Response(sold_data)


class WarehouseSaleProductGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = WarehouseSaleProduct.objects.all()
    serializer_class = WarehouseSaleProductSerializer


class WarehouseSaleProductGetEndsWith(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = WarehouseSaleProduct.objects.all()
    serializer_class = WarehouseSaleProductSerializer

    def get(self, request, *args, **kwargs):
        sale = get_object_or_404(WarehouseSaleProduct, id__endswith=kwargs['pk'])
        sale_ser = WarehouseSaleProductSerializer(sale).data
        return sale_ser
