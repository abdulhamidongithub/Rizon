from datetime import datetime

from django.shortcuts import render
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.employee_per import IsEmployee
from warehouses.models import WarehouseProduct, Warehouse
from warehouses.serializers import WarehouseProductSerializer, PostWarehouseProductSerializer
from .models import *
from .serializers import *


def view_product_template(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, "index.html", {"product": product})


# Products
class ProductGetOne(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Product.objects.filter(deleted=False)
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        product = Product.objects.get(name=kwargs['name'])
        product_ser = ProductSerializer(product)

        return Response({"product": product_ser.data})

class ProductsTransferData(APIView):
    def post(self, request):
        product = Product.objects.create(
            name=request.data.get("name"),
            price=request.data.get("price"),
            extraPrice=request.data.get("extraPrice"),
            about=request.data.get("about"),
            date=request.data.get("date"),
        )
        product_Ser = ProductSerializer(product).data
        return Response(product_Ser)


class ProductListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsEmployee]
    queryset = Product.objects.filter(deleted=False)
    serializer_class = ProductSerializer


    def create(self, request, *args, **kwargs):
        ser = ProductSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)

class ProductGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = Product.objects.filter(deleted=False)
    serializer_class = ProductSerializer

    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            product = get_object_or_404(Product, id=kwargs['pk'])
            product.deleted=True
            product.save()
            return Response({"detail": "deleted"})
        else:
            return Response({"detail": "You do not have permission to perform this action."})

    def put(self, request, *args, **kwargs):
        if request.user.is_staff:
            ser = ProductSerializer2(data=request.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)
            else:
                return Response({
                    "detail": "Data is invalid.",
                    "error": ser.errors
                })
        else:
            return Response({"detail": "You do not have permission to perform this action."})


class ProductDistributionList(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = WarehouseProduct.objects.all()
    serializer_class = WarehouseProductSerializer
    http_method_names = ("get", "post")

    def post(self, request, *args, **kwargs):
        ser = PostWarehouseProductSerializer(data=request.data)
        if ser.is_valid():
            warehouse = get_object_or_404(Warehouse, id=ser.data.get("warehouse"))
            product = get_object_or_404(Product, id=ser.data.get("product"))

            WarehouseProduct.objects.create(
                warehouse=warehouse,
                product=product,
                paid=ser.data.get("paid"),
                summa=product.price * ser.data.get("amount"),
                amount=ser.data.get("amount")
            )
            # ser.save()
            return Response(ser.data)
        else:
            return Response(ser.errors)

class ProductOrderCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ProductOrder.objects.all()
    serializer_class = ProductOrderSerializer

    def create(self, request, *args, **kwargs):
        ser = PostProductOrderSerializer(data=request.data)
        if ser.is_valid():
            user = get_object_or_404(User, username=request.user.username)
            product = get_object_or_404(Product, id=ser.data.get("product"))
            warehouse = get_object_or_404(Warehouse, id=ser.data.get("warehouse"))
            ProductOrder.objects.create(
                user = user,
                product = product,
                warehouse = warehouse,
                amount = ser.data.get("amount"),
            )
            return Response(ser.data)
        else:
            return Response(ser.errors)


class ProductOrderGetUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = ProductOrder.objects.all()
    serializer_class = ProductOrderSerializer



# class ProductDiscountAPI(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]
#
#     def create(self, request, pk):
#         ser = PostProductDiscountSerializer(data=request.data)
#         if ser.is_valid():
#             Product.object.filter(id=pk).update(discount=request.data.get("discount"))
#             return Response({
#                 "success": True,
#                 "message": "Aksiya belgilandi !"
#             })
#         else:
#             raise ValidationError({
#                 "success": False,
#                 "message": "Aksiya belgilab bo'lmadi !"
#             })

# class ProductDiscountDestroyAPI(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]
#
#     def create(self, request, pk):
#         Product.object.get(id=pk).update(discount=0)
#         return Response({
#             "success": True,
#             "message": "Aksiya bekor qilindi !"
#         })



class ProductDiscountListCreate(APIView):
    permission_classes = [IsAuthenticated, ]
    queryset = ProductDiscount.objects.all()
    serializer_class = ProductDiscountSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            ser = PostProductDiscountSerializer2(data=request.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)
            return Response(ser.errors)
        return Response({"success": False})

    def get(self, request):
        discounts = ProductDiscount.objects.filter(endDate__gte=datetime.today(), startDate__lte=datetime.today())
        discounts_ser = ProductDiscountSerializer(discounts, many=True).data
        return Response(discounts_ser)


class ProductDiscountCreate(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ProductDiscount.objects.all()
    serializer_class = ProductDiscountSerializer

    def post(self, request, *args, **kwargs):
        ser = PostProductDiscountSerializer2(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)



class ProductDiscountGetDestroy(RetrieveAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = ProductDiscount.objects.all()
    serializer_class = ProductDiscountSerializer


class LandingProductOrderCreate(CreateAPIView):
    # permission_classes = [IsAuthenticated,]
    queryset = LandingProductOrder.objects.all()
    serializer_class = LandingProductOrder
