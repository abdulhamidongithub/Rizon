from datetime import datetime

import requests
from django.db.models import Sum
from django.shortcuts import render
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from others.rv_ball import rv_ball
from others.views import totally_info
from products.models import ProductDiscount
from products.serializers import forLandiingPoductSerializer
from users.models import VIA_PHONE, MEDIC, DONE
from warehouses.models import WarehouseSaleProduct
from .medic_permissions import IsMedic
from .models import *
from .serializers import *
from rest_framework.status import HTTP_400_BAD_REQUEST

# class MedicTransferData(APIView):
#     def post(self, request):
#         try:
#             user = User.objects.create(
#                 username=request.data.get("username"),
#                 password=request.data.get("password"),
#                 first_name=request.data.get("first_name"),
#                 last_name=request.data.get("last_name"),
#                 passport=request.data.get("passport"),
#                 user_roles=MEDIC,
#                 auth_type=VIA_PHONE,
#                 auth_status=DONE,
#                 phone_number=request.data.get("phone_number"),
#                 # user_id=request.data.get("user_id"),
#                 address=request.data.get("address"),
#                 phoneNumTwo=request.data.get("phoneNumTwo"),
#                 dateOfBirth=request.data.get("dateOfBirth"),
#                 date=request.data.get("date")
#             )
#             medic = Medic.objects.create(
#                 user = user,
#                 degree = request.data.get("degree"),
#                 university = request.data.get("university"),
#                 bio = request.data.get("bio"),
#                 date = request.data.get("date"),
#             )
#
#             medic_ser = MedicSerializer(medic).data
#             return Response(medic_ser)
#
#         except:
#             return Response({
#                 "success": False,
#                 "message": f"{request.data.get('user_id')}",
#                 "first_name": f"{request.data.get('first_name')}"
#             })


class MedicSalaryPaymentsTransferData(APIView):
    http_method_names = ("post", )

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            salary = MedSalaryPayment.objects.create(
                medic=Medic.objects.get(user__username=data['medic']),
                paid=data['paid'],
                date=data['date'],
                dateTime=data['dateTime']
            )
            salary = MedSalarySerializer(salary).data
            return Response(
                {
                    "success": True,
                    "message": salary
                }
            )
        except:
            return Response(
                {
                    "success": False,
                    "message": "#################################################################################################################\n" +
                              "##################################################################################################################\n" +
                              "###################################################################################################################\n" +
                              "###################################################################################################################\n" +
                              "###################################################################################################################\n" +
                              "##########################################################"
                })



class MedProductDestroy(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = MedProduct.objects.all()
    serializer_class = MedProductSerializer

    def delete(self, request, *args, **kwargs):
        m_product = MedProduct.objects.get(medic__id=kwargs['pk'], product__id=kwargs['p_id'])

        return Response({"detail": "deleted"})





# Medic
class MedicListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Medic.objects.filter(deleted=False)
    serializer_class = MedicSerializer

    def get(self, request, *args, **kwargs):
        medics_data = Medic.objects.filter(deleted=False)
        medics_data_ser = insteadGetMeddicInfoSerializer(medics_data, many=True)

        medics_full_data = []
        for medic in medics_data_ser:
            medic_products = MedProduct.objects.filter(medic__id=medic['id'], deleted=False)
            medic_products_ser = MedProductSerializer(medic_products, many=True).data

            med_sum = 0
            for product in medic_products_ser:
                sales_summa = WarehouseSaleProduct.objects.filter(product=product['product']['id']).aggregate(Sum('summa'))

                if sales_summa['summa__sum'] is not None:
                    med_sum += sales_summa['summa__sum'] / rv_ball['BALL'] * (product['bonus'] / 100) * rv_ball['RV']

            # medic_full_data = {"medic": medic, "salary": round(med_sum, 2), "med_products": medic_products_ser}
            # medic_data = {}
            # print(f"{medic=}")
            # for k, v in medic:
            #     medic_data[k] = v
            med_paid = MedSalaryPayment.objects.filter(medic__id=medic['id']).aggregate(Sum('paid'))
            med_paid_sum = med_paid['paid__sum'] if med_paid['paid__sum'] is not None else 0

            medic["salary"] = round(med_sum - med_paid_sum, 2)
            medic["med_products"] = medic_products_ser

            medics_full_data.append(medic)

        total_info = totally_info("20")
        total_info.update({"medics": medics_full_data})

        return Response(total_info)

    def create(self, request, *args, **kwargs):
        try:
            User.objects.get(username=request.data.get("username"))
            return Response({
                "success": False,
                "message": "Ushbu username allaqachon mavjud."
            }, status=HTTP_400_BAD_REQUEST)
        except:
            pass
        try:
            User.objects.get(username=request.data.get("phone_number"))
            return Response({
                "success": False,
                "message": "Ushbu telefon raqam allaqachon mavjud."
            }, status=HTTP_400_BAD_REQUEST)
        except:
            pass
        try:
            user = User.objects.create(
                username=request.data.get("username"),
                password=request.data.get("password"),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                passport=request.data.get("passport"),
                user_roles=MEDIC,
                auth_type=VIA_PHONE,
                auth_status=DONE,
                phone_number=request.data.get("phone_number"),
                user_id=request.data.get("user_id"),
                address=request.data.get("address"),
                phoneNumTwo=request.data.get("phoneNumTwo"),
                dateOfBirth=request.data.get("dateOfBirth")
            )
            medic = Medic.objects.create(
                user=user,
                degree=request.data.get("degree"),
                university=request.data.get("university"),
                bio=request.data.get("bio"),
                date=request.data.get("date")
            )

            medic_ser = MedicSerializer(medic).data
            return Response(medic_ser)

        except:
            return Response({
                "success": False,
                "message": f"Med konsultant qo'shishda xatolikka yo'l qo'yildi.",
                "first_name": f"{request.data.get('first_name')}"
            })


class MedicListByMonth(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Medic.objects.filter(deleted=False)
    serializer_class = MedicSerializer

    def get(self, request, *args, **kwargs):
        medics_data = Medic.objects.filter(deleted=False)
        medics_data_ser = insteadGetMeddicInfoSerializer(medics_data, many=True)

        medics_full_data = []
        for medic in medics_data_ser:
            medic_products = MedProduct.objects.filter(medic__id=medic['id'], deleted=False)
            medic_products_ser = MedProductSerializer(medic_products, many=True).data

            med_sum = 0
            for product in medic_products_ser:
                sales_summa = WarehouseSaleProduct.objects.filter(product=product['product']['id'], dateTime__startswith=kwargs['month']).aggregate(Sum('summa'))

                if sales_summa['summa__sum'] is not None:
                    med_sum += sales_summa['summa__sum'] / rv_ball['BALL'] * (product['bonus'] / 100) * rv_ball['RV']

            # medic_full_data = {"medic": medic, "salary": round(med_sum, 2), "med_products": medic_products_ser}
            # medic_data = {}
            # print(f"{medic=}")
            # for k, v in medic:
            #     medic_data[k] = v
            medic["salary"] = round(med_sum, 2)
            medic["med_products"] = medic_products_ser

            medics_full_data.append(medic)

        total_info = totally_info(kwargs['month'])
        total_info.update({"medics": medics_full_data})

        return Response(total_info)



class MedicGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Medic.objects.filter(deleted=False)
    serializer_class = MedicSerializer

    def get(self, request, *args, **kwargs):
        medic = get_object_or_404(Medic, id=kwargs['pk'])
        medic_ser = insteadGetMeddicInfoSerializer(medic)

        medic_products = MedProduct.objects.filter(medic__id=kwargs['pk'], deleted=False)
        medic_products_ser = MedProductSerializer(medic_products, many=True).data

        medic_salary_payments = MedSalaryPayment.objects.filter(medic=medic)
        medic_salary_payments_ser = MedSalarySerializer(medic_salary_payments, many=True).data

        med_sum = 0
        for product in medic_products_ser:
            sales_summa = WarehouseSaleProduct.objects.filter(product=product['product']['id']).aggregate(Sum('summa'))

            if sales_summa['summa__sum'] is not None:
                med_sum += sales_summa['summa__sum'] / rv_ball['BALL'] * (product['bonus'] / 100) * rv_ball['RV']

        med_paid = MedSalaryPayment.objects.filter(medic=medic).aggregate(Sum('paid'))
        med_paid_sum = med_paid['paid__sum'] if med_paid['paid__sum'] is not None else 0

        med_sum = round(med_sum - med_paid_sum, 2)

        return Response({"share_of_sales_percent": 2, "medic": medic_ser, "total_salary": med_sum, "medic_products": medic_products_ser, "salary_payments": medic_salary_payments_ser})


    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            medic = get_object_or_404(Medic, id=kwargs['pk'])
            medic.deleted=True
            medic.save()
            return Response({"detail": "deleted"})
        else:
            return Response({"detail": "You are not provided this action"})


class MedicGetOne(RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = Medic.objects.filter(deleted=False)
    serializer_class = MedicSerializer


    def get(self, request, *args, **kwargs):
        medic = Medic.objects.get(user_id=kwargs['pk'])
        medic_ser = MedicSerializer(medic)
        return Response({"medic": medic_ser.data})


class MedicDeleteOne(DestroyAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = Medic.objects.filter(deleted=False)
    serializer_class = MedicSerializer


    def delete(self, request, *args, **kwargs):
        Medic.objects.filter(user_id=kwargs['pk']).update(deleted=False)
        return Response(
            {
                "success": True,
                "message": "Medic has been deleted."
            }
        )



# class MedicGetSalary(APIView): # RetrieveAPIView
#     permission_classes = [IsAuthenticated, IsAdminUser]
#     queryset = Medic.objects.all()
#     serializer_class = MedicSerializer

#     def get(self, request, *args, **kwargs):
#         medic = get_object_or_404(Medic, id=kwargs['pk'])
#         med_ser = insteadGetMeddicInfoSerializer(medic)
#         date = kwargs['date']
#         medic_products = MedProduct.objects.filter(medic__id=kwargs['pk'], deleted=False)
#         medic_products_ser = MedProductSerializer(medic_products, many=True).data

#         payments_sum = MedSalaryPayment.objects.filter(medic=medic).aggregate(Sum('paid'))
#         total_paid = payments_sum['paid__sum'] if payments_sum['paid__sum'] is not None else 0

#         total_med_sum = 0
#         med_sum = 0
#         for product in medic_products_ser:
#             sales_summa = WarehouseSaleProduct.objects.filter(product=product['product']['id'], dateTime__startswith=date).aggregate(Sum('summa'))
#             total_sales_summa = WarehouseSaleProduct.objects.filter(product=product['product']['id']).aggregate(Sum('summa'))

#             if sales_summa['summa__sum'] is not None:
#                 med_sum += sales_summa['summa__sum'] / rv_ball['BALL'] * (product['bonus']/100) * rv_ball['RV']

#             if total_sales_summa['summa__sum'] is not None:
#                 total_med_sum += sales_summa['summa__sum'] / rv_ball['BALL'] * (product['bonus']/100) * rv_ball['RV']

#         paid = MedSalaryPayment.objects.filter(medic=medic, date__startswith=date).aggregate(Sum('paid'))
#         paid = paid['paid__sum'] if paid['paid__sum'] is not None else 0

#         return Response({"medic": med_ser, "salary": round(med_sum, 2), "paid": paid, "forMonth": str(date)[:7], "fee": round(total_med_sum - total_paid, 2), "total_paid": round(total_paid, 2), "total_salary": round(total_med_sum, 2)})

class MedicGetSalary(APIView): # RetrieveAPIView
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Medic.objects.all()
    serializer_class = MedicSerializer

    def get(self, request, *args, **kwargs):
        medic = get_object_or_404(Medic, id=kwargs['pk'])
        med_ser = insteadGetMeddicInfoSerializer(medic)
        date = kwargs['date']
        medic_products = MedProduct.objects.filter(medic__id=kwargs['pk'], deleted=False)
        medic_products_ser = MedProductSerializer(medic_products, many=True).data

        payments_sum = MedSalaryPayment.objects.filter(medic=medic).aggregate(Sum('paid'))
        total_paid = payments_sum['paid__sum'] if payments_sum['paid__sum'] is not None else 0

        med_products = {"products": [], "amount": 0, "summa": 0}
        total_med_sum = 0
        med_sum = 0
        for product in medic_products_ser:
            sales_summa = WarehouseSaleProduct.objects.filter(product=product['product']['id'], dateTime__startswith=date).aggregate(Sum('summa'))
            total_sales_summa = WarehouseSaleProduct.objects.filter(product=product['product']['id']).aggregate(Sum('summa'))

            sales_amount = WarehouseSaleProduct.objects.filter(product=product['product']['id'], dateTime__startswith=date).aggregate(Sum('amount'))
            sales_amount_sum = sales_amount['amount__sum'] if sales_amount['amount__sum'] is not None else 0

            if sales_summa['summa__sum'] is not None:
                med_sum += sales_summa['summa__sum'] / rv_ball['BALL'] * (product['bonus']/100) * rv_ball['RV']

            if total_sales_summa['summa__sum'] is not None:
                total_med_sum += sales_summa['summa__sum'] / rv_ball['BALL'] * (product['bonus']/100) * rv_ball['RV']

            med_products['products'].append(
                {
                    "product": product['product']['name'],
                    "amount": sales_amount_sum
                }
            )
            summa_1 = sales_summa['summa__sum'] if sales_summa['summa__sum'] is not None else 0
            med_products['amount'] += sales_amount_sum
            med_products['summa'] += summa_1

        paid = MedSalaryPayment.objects.filter(medic=medic, date__startswith=date).aggregate(Sum('paid'))
        paid = paid['paid__sum'] if paid['paid__sum'] is not None else 0

        return Response(
            {
                "medic": med_ser,
                "salary": round(med_sum, 2),
                "paid": paid,
                "forMonth": str(date)[:7],
                "fee": round(total_med_sum - total_paid, 2),
                "total_paid": round(total_paid, 2),
                "total_salary": round(total_med_sum, 2),
                "med_products": med_products
            })




# Med Product
# class MedGetProducts(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]
#     queryset = MedProduct.objects.all()
#     serializer_class = MedProductSerializer
#
#     def get(self, request, *args, **kwargs):
#         medic = Medic.objects.get(id=kwargs['pk'])
#         med_products = MedProduct.objects.filter(medic__id=kwargs['pk'])
#         med_products_ser = MedProductSerializer(med_products, many=True)
#         return Response({"medic": medic, "medic_products": med_products_ser.data})

from rest_framework.generics import ListCreateAPIView
class MedProductListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = MedProduct.objects.all()
    serializer_class = MedProductSerializer

    # def post(self, request):
    #     ser = PostMedProductSerializer2(data=request.data)
    #     if ser.is_valid():
    #         ser.save()
    #         return Response(ser.data)
    #     else:
    #         return Response(ser.errors)
    # def post(self, request):
    #     medic = get_object_or_404(Medic, id=request.data.get("medic"))
    #     product = get_object_or_404(Medic, id=request.data.get("product"))
    #     m = MedProduct.objects.create(
    #         medic=medic,
    #         product=product
    #     )
    #     m_ser = MedProductSerializer(m).data
    #     return Response(m_ser)


class MedProductPost(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = MedProduct.objects.all()
    serializer_class = MedProductSerializer

    def post(self, request, **kwargs):
        ser = PostMedProductSerializer2(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        else:
            return Response(ser.errors)
    # def post(self, request):
    #     medic = get_object_or_404(Medic, id=request.data.get("medic"))
    #     product = get_object_or_404(Medic, id=request.data.get("product"))
    #     m = MedProduct.objects.create(
    #         medic=medic,
    #         product=product
    #     )
    #     m_ser = MedProductSerializer(m).data
    #     return Response(m_ser)



class MedProductGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = MedProduct.objects.filter(deleted=False)
    serializer_class = MedProductSerializer

    def delete(self, request, *args, **kwargs):
        m_product = MedProduct.objects.get(product=kwargs['p_id'], medic__id=kwargs['pk'])
        m_product.deleted=True
        m_product.save()
        return Response({"detail": "deleted"})

    def get(self, request, *args, **kwargs):
        m_product = MedProduct.objects.get(product=kwargs['p_id'], medic__id=kwargs['pk'])
        m_product_ser = MedProductSerializer(m_product).data
        return Response(m_product_ser)

    def update(self, request, *args, **kwargs):
        m_product = MedProduct.objects.filter(product=kwargs['p_id'], medic__id=kwargs['pk']).update(**kwargs)
        m_product_ser = MedProductSerializer(m_product).data
        return Response(m_product_ser)



class MedGetProducts(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = MedProduct.objects.all()
    serializer_class = MedProductSerializer

    def get(self, request, *args, **kwargs):
        medic = Medic.objects.get(id=kwargs['pk'])
        med_products = MedProduct.objects.filter(medic=medic)
        med_products_ser = MedProductSerializer(med_products, many=True)
        medic_ser = MedicSerializer(medic).data
        return Response({"medic": medic_ser, "medic_products": med_products_ser.data})


# Med Salary
class MedSalaryPaymentListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = MedSalaryPayment.objects.all()
    serializer_class = MedSalarySerializer


    def create(self, request, *args, **kwargs):
        ser = PostMedSalarySerializer(data=request.data)
        if ser.is_valid():
            MedSalaryPayment.objects.create(
                medic=Medic.objects.get(id=ser.data.get("medic")),
                paid=ser.data.get("paid"),
                date=str(request.data.get("date"))+"-10"
            )
            # ser.save()
            return Response(ser.data)
        else:
            return Response(ser.errors)


class MedSalaryPaymentGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = MedSalaryPayment.objects.all()
    serializer_class = MedSalarySerializer


class MedSalaryPaymentGetPayments(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Medic.objects.all()
    serializer_class = MedicSerializer

    def get(self, request, *args, **kwargs):
        medic = get_object_or_404(Medic, id=kwargs['pk'])
        payments = MedSalaryPayment.objects.filter(medic=medic).order_by("-date")
        payments_ser = MedSalarySerializer(payments, many=True).data

        return Response({
            "payments": payments_ser
        })


class MedicMainPageAPI(APIView):
    permission_classes = [IsAuthenticated, IsMedic]

    def get(self, request, month):
        medic = get_object_or_404(Medic, user=request.user)
        medic_Ser = insteadGetMeddicInfoSerializer(medic)

        medic_products = MedProduct.objects.filter(medic__id=medic_Ser['id'])
        medic_products_Ser = MedProductSerializer(medic_products, many=True).data

        sales_summa = 0

        for product in medic_products_Ser:
            sales = WarehouseSaleProduct.objects.filter(product__id=product["product"]['id'], dateTime__startswith=month).aggregate(Sum('summa'))
            sales_summa += sales['summa__sum'] if sales['summa__sum'] is not None else 0

        # salary = sales_summa / rv_ball['BALL'] * (medic_Ser['share_of_sales_percent']/100) * rv_ball['RV']
        percent = medic_Ser['share_of_sales_percent'] if medic_Ser['share_of_sales_percent'] is not None else 4
        try:
            salary = round(sales_summa / rv_ball['BALL'] * (percent/100) * rv_ball['RV'], 2)
        except:
            salary = 0

        salary_payments_history = MedSalaryPayment.objects.filter(medic=medic)
        salary_payments_history_ser = MedSalarySerializer(salary_payments_history, many=True).data

        products = MedProduct.objects.filter(medic=medic)
        products_Ser = ForOthersMedProductSerializer(products, many=True).data

        products_data = []
        for pr in products_Ser:
            products_data.append(pr['product'])

        ins_payments_Data = []
        for i in salary_payments_history_ser:
            i['products'] = products_data
            ins_payments_Data.append(i)

        discount_products = ProductDiscount.objects.filter(endDate__gte=datetime.today())
        discount_products_Ser = forLandiingPoductSerializer(discount_products, many=True)

        discounts = []

        for product in discount_products_Ser:
            product['discount'] = f"{product['amount']}+{product['discount']} aksiya"
            product['lifetime'] = f"Chegirma muddati {str(product['startDate'])[:10]} sanasidan {str(product['endDate'])[:10]} sanasiga qadar davom etadi."
            discounts.append(product)

        return Response({
            "total_income": salary,
            "salary_history": ins_payments_Data,
            "discounts": discounts
        })


class MedicProfilePageAPI(APIView):
    permission_classes = [IsAuthenticated, IsMedic]

    def get(self, request):
        medic = get_object_or_404(Medic, user=request.user)
        medic_Ser = insteadGetMeddicInfoSerializer(medic)

        medic_products = MedProduct.objects.filter(medic=medic, deleted=False)
        medic_products_Ser = MedProductSerializer(medic_products, many=True).data

        sales_summa = 0

        for product in medic_products_Ser:
            sales = WarehouseSaleProduct.objects.filter(product__id=product["product"]['id']).aggregate(Sum('summa'))
            sales_summa += sales['summa__sum'] if sales['summa__sum'] is not None else 0

        # total_salary = sales_summa / rv_ball['BALL'] * (medic_Ser['share_of_sales_percent']/100) * rv_ball['RV']
        percent = medic_Ser['share_of_sales_percent'] if medic_Ser['share_of_sales_percent'] is not None else 4
        try:
            total_salary = round(sales_summa / rv_ball['BALL'] * (percent/100) * rv_ball['RV'], 2)
        except:
            total_salary = 0

        salary_payments_sum = MedSalaryPayment.objects.filter(medic=medic).aggregate(Sum('paid'))
        salary_payments_paid = salary_payments_sum['paid__sum'] if salary_payments_sum['paid__sum'] is not None else 0

        salary_payments_history = MedSalaryPayment.objects.filter(medic=medic)
        salary_payments_history_ser = MedSalarySerializer(salary_payments_history, many=True).data

        products = MedProduct.objects.filter(medic=medic)
        products_Ser = ForOthersMedProductSerializer(products, many=True).data

        products_data = []
        for pr in products_Ser:
            products_data.append(pr['product'])

        ins_payments_Data = []
        for i in salary_payments_history_ser:
            i['products'] = products_data
            ins_payments_Data.append(i)

        return Response({
            "medic": medic_Ser,
            "medic_products": medic_products_Ser,
            "remaining_salary": total_salary - salary_payments_paid,
            "salary_history": ins_payments_Data
        })


class MedicStatisticsPageAPI(APIView):
    permission_classes = [IsAuthenticated, IsMedic]

    def get(self, request, month):
        medic = get_object_or_404(Medic, user=request.user)
        medic_Ser = insteadGetMeddicInfoSerializer(medic)

        medic_products = MedProduct.objects.filter(medic=medic)
        medic_products_Ser = MedProductSerializer(medic_products, many=True).data

        sales_summa = 0

        for product in medic_products_Ser:
            sales = WarehouseSaleProduct.objects.filter(product__id=product["product"]['id']).aggregate(Sum('summa'))
            sales_summa += sales['summa__sum'] if sales['summa__sum'] is not None else 1

        # total_salary = sales_summa / rv_ball['BALL'] * (medic_Ser['share_of_sales_percent']/100) * rv_ball['RV']
        percent = medic_Ser['share_of_sales_percent'] if medic_Ser['share_of_sales_percent'] is not None else 4
        try:
            total_salary = round(sales_summa / rv_ball['BALL'] * (percent/100) * rv_ball['RV'], 2)
        except:
            total_salary = 0

        month_product_sales_data = {}

        month_product_sales = WarehouseSaleProduct.objects.all().aggregate(Sum('amount'))
        product_sale_amount_divide = month_product_sales['amount__sum'] if month_product_sales['amount__sum'] is not None else 1

        for product in medic_products_Ser:
            product_sale_amount = WarehouseSaleProduct.objects.filter(product__id=product["product"]['id'], dateTime__startswith=month).aggregate(Sum('amount'))
            product_sale_amount = product_sale_amount['amount__sum'] if product_sale_amount['amount__sum'] is not None else 0
            product_sale_summa = WarehouseSaleProduct.objects.filter(product__id=product["product"]['id'], dateTime__startswith=month).aggregate(Sum('summa'))
            product_sale_summa = product_sale_summa['summa__sum'] if product_sale_summa['summa__sum'] is not None else 0
            try:
                sale_sum = round(product_sale_amount / product_sale_amount_divide * 100, 1)
            except:
                sale_sum = 0

            month_product_sales_data[f"{product['product']['name']}"] = {"product_sales_percent": sale_sum, 'product_sale_amount': product_sale_amount, 'product_sale_summa': product_sale_summa}


        return Response({
            "total_income": total_salary,
            "medic_products": medic_products_Ser,
            "product_sales_data": month_product_sales_data
        })


class MedicProductsPageAPI(APIView):
    permission_classes = [IsAuthenticated, IsMedic]

    def get(self, request):
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
        })
