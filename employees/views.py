import math
from datetime import datetime

from django.db.models import Sum
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST

from others.rv_ball import rv_ball
from others.serializers import UseBonusAccountSerializer
from products.models import ProductOrder, Product, ProductDiscount
from products.serializers import ProductOrderSerializer, ProductSerializer, ProductDiscountSerializer, \
    forLandiingPoductSerializer
from users.calculations import get_all_shajara, user_all_bonuses_test
from users.models import UsersSalaryPayment, VIA_PHONE, EMPLOYEE, BonusAccount, CASHBACK, VOUCHER
from users.serializers import UsersSerializer, UsersSalarySerializer, AdminBonusAccountSerializer
from warehouses.models import WarehouseSaleProduct, WarehouseProduct, Warehouse, WAREHOUSE
from warehouses.serializers import WarehouseProductSerializer, WarehouseSaleProductSerializer, \
    PostWarehouseSaleProductSerializer2
from .employee_per import IsEmployee
from .serializers import *


class EmployeeSalaryPaymentsTransferAPIView(APIView):
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            salary = EmployeeSalaryPayments.objects.create(
                employee=Employee.objects.get(user__username=data['employee']),
                paid=data['paid'],
                date=data['date'],
                paymentDate=data['paymentDate']
            )
            salary = EmployeeSalarySerializer(salary).data
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

class EmployeeTransferData(APIView):
    def post(self, request):
        try:
            user = User.objects.create(
                username=request.data.get("username"),
                password=request.data.get("password"),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                passport=request.data.get("passport"),
                user_roles=EMPLOYEE,
                auth_type=VIA_PHONE,
                auth_status=DONE,
                phone_number=request.data.get("phone_number"),
                # user_id=request.data.get("user_id"),
                address=request.data.get("address"),
                phoneNumTwo=request.data.get("phoneNumTwo"),
                dateOfBirth=request.data.get("dateOfBirth"),
                date=request.data.get("date")
            )
            warehouse = Warehouse.objects.get(name=request.data.get("warehouse"))
            employee = Employee.objects.create(
                user = user,
                warehouse = warehouse,
                date = request.data.get("date"),
            )

            employee_ser = EmployeeSerializer(employee).data
            return Response(employee_ser)

        except:
            return Response({
                "success": False,
                "message": f"{request.data.get('user_id')}",
                "first_name": f"{request.data.get('first_name')}"
            })
########################################################################################################################



def head_info(request):
    from datetime import datetime
    warehouse_income = WarehouseSaleProduct.objects.filter(employee__user=request.user, dateTime__startswith=str(datetime.today())[:7]).aggregate(Sum('summa'))
    warehouss_income_sum = warehouse_income['summa__sum'] if warehouse_income['summa__sum'] is not None else 0
    total_users = User.objects.all().count()
    all_coupon = warehouss_income_sum // rv_ball['BALL']

    return {
        "total_sales_summa": warehouss_income_sum,
        "total_users": total_users,
        "total_coupon": all_coupon,
    }


class EmployeeCreateFRBotAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)


    def post(self, request):
        try:
            user = User.objects.create(
                username=request.data.get("username"),
                password=request.data.get("password"),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                passport=request.data.get("passport"),
                user_roles=EMPLOYEE,
                auth_type=VIA_PHONE,
                auth_status=DONE,
                phone_number=request.data.get("phone_number"),
                user_id=request.data.get("user_id"),
                address=request.data.get("address"),
                phoneNumTwo=request.data.get("phoneNumTwo"),
                dateOfBirth=request.data.get("dateOfBirth")
            )
            warehouse = Warehouse.objects.get(id=request.data.get("warehouse"))
            employee = Employee.objects.create(
                user=user,
                warehouse=warehouse
            )

            employee_ser = EmployeeSerializer(employee).data
            return Response(employee_ser)

        except:
            return Response({
                "success": False,
                "message": f"{request.data.get('user_id')}",
                "first_name": f"{request.data.get('first_name')}"
            }, status=400)

#######################################################################################################################




class EmployeeGetOne(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Employee.objects.filter(deleted=False)
    serializer_class = EmployeeSerializer


    def get(self, request, *args, **kwargs):
        employee = Employee.objects.get(user=User.objects.get(user_id=kwargs['pk']))
        employee_ser = EmployeeSerializer(employee)
        return Response({"employee": employee_ser.data})


# class EmployeeListCreate(ListCreateAPIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]
#     queryset = Employee.objects.filter(deleted=False)
#     serializer_class = EmployeeSerializer
#
#     def create(self, request, *args, **kwargs):
#         # ser = PostEmployeeSerializer(data=request.data)
#         # if ser.is_valid():
#         #     ser.save()
#         #     return Response(ser.data)
#         # else:
#         #     return Response(ser.errors)
#         try:
#             User.objects.get(username=request.data.get("username"))
#             return Response({
#                 "success": False,
#                 "message": "Ushbu username allaqachon mavjud."
#             }, status=HTTP_400_BAD_REQUEST)
#         except:
#             pass
#         try:
#             User.objects.get(username=request.data.get("phone_number"))
#             return Response({
#                 "success": False,
#                 "message": "Ushbu telefon raqam allaqachon mavjud."
#             }, status=HTTP_400_BAD_REQUEST)
#         except:
#             pass
#         try:
#             user = User.objects.create(
#                 username=request.data.get("username"),
#                 password=request.data.get("password"),
#                 first_name=request.data.get("first_name"),
#                 last_name=request.data.get("last_name"),
#                 passport=request.data.get("passport"),
#                 user_roles=EMPLOYEE,
#                 auth_type=VIA_PHONE,
#                 auth_status=DONE,
#                 phone_number=request.data.get("phone_number"),
#                 # user_id=request.data.get("user_id"),
#                 address=request.data.get("address"),
#                 phoneNumTwo=request.data.get("phoneNumTwo"),
#                 dateOfBirth=request.data.get("dateOfBirth"),
#             )
#             warehouse = Warehouse.objects.get(name=request.data.get("warehouse"))
#             employee = Employee.objects.create(
#                 user = user,
#                 warehouse = warehouse
#             )
#
#             employee_ser = insteadGetEmployeeInfoSerializer(employee)
#             return Response(employee_ser)
#
#         except:
#             return Response({
#                 "success": False,
#                 "message": f"Xodim qo'shishda xatolikka yo'l qo'yildi.",
#                 "first_name": f"{request.data.get('first_name')}"
#             })


class EmployeeListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Employee.objects.filter(deleted=False)
    serializer_class = CreateEmployeeSerializer

    def create(self, request, *args, **kwargs):
        new_employee_ser = CreateEmployeeSerializer(data=request.data)
        if new_employee_ser.is_valid():
            try:
                User.objects.get(phone_number=request.data.get("phone_number"))
                return Response({
                    "success": False,
                    "message": "Ushbu telefon raqam allaqachon mavjud."
                }, status=HTTP_400_BAD_REQUEST)
            except:
                pass
            try:
                User.objects.get(username=request.data.get("username"))
                return Response({
                    "success": False,
                    "message": "Ushbu username allaqachon mavjud."
                }, status=HTTP_400_BAD_REQUEST)
            except:
                pass
            try:
                User.objects.get(passport=request.data.get("passport"))
                return Response({
                    "success": False,
                    "message": "Passport ma'lumotlari xato kiritildi."
                }, status=HTTP_400_BAD_REQUEST)
            except:
                pass
            new_user_id = int("".join([str(random.randint(0, 10000) % 10) for _ in range(10)]))
            while User.objects.filter(user_id=new_user_id):
                new_user_id = new_user_id + random.randint(1, 10000)
            new_user_id = new_user_id
            try:
                user = User.objects.create(
                    username=request.data.get("username"),
                    password=request.data.get("password"),
                    first_name=request.data.get("first_name"),
                    last_name=request.data.get("last_name"),
                    passport=request.data.get("passport"),
                    user_roles=EMPLOYEE,
                    auth_type=VIA_PHONE,
                    auth_status=DONE,
                    phone_number=request.data.get("phone_number"),
                    user_id=new_user_id,
                    address=request.data.get("address"),
                    phoneNumTwo=request.data.get("phoneNumTwo"),
                    dateOfBirth=request.data.get("dateOfBirth"),
                )
                warehouse = Warehouse.objects.get(id=request.data.get("warehouse"))
                employee = Employee.objects.create(
                    user = user,
                    warehouse = warehouse
                )

                employee_ser = insteadGetEmployeeInfoSerializer(employee)
                return Response(employee_ser)

            except:
                return Response({
                    "success": False,
                    "message": f"Xodim qo'shishda xatolikka yo'l qo'yildi.",
                    "first_name": f"{request.data.get('first_name')}"
                })
        else:
            return Response(new_employee_ser.errors)


    def get(self, request, *args, **kwargs):
        employees_Data = Employee.objects.filter(deleted=False)
        employees_list = []
        for employee in employees_Data:
            employee_ser = insteadGetEmployeeInfoSerializer(employee)
            employees_list.append(employee_ser)

        return Response(employees_list)


class EmployeeGetUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Employee.objects.filter(deleted=False)
    serializer_class = EmployeeSerializer

    def delete(self, request, *args, **kwargs):
        employee_user = Employee.objects.filter(id=kwargs['pk'])
        if employee_user:
            employee = employee_user[0]
        else:
            employee = get_object_or_404(Employee, user=get_object_or_404(User, id=kwargs['pk']))

        employee.deleted=True
        employee.save()
        return Response({"detail": "deleted"})

    def get(self, request, *args, **kwargs):
        employee_user = Employee.objects.filter(id=kwargs['pk'])
        if employee_user:
            employee = employee_user[0]
        else:
            employee = get_object_or_404(Employee, user=get_object_or_404(User, id=kwargs['pk']))

        employee_ser = insteadGetEmployeeInfoSerializer(employee)

        payments = EmployeeSalaryPayments.objects.filter(employee=employee)
        payments_ser = EmployeeSalarySerializer(payments, many=True).data

        payments_sum = EmployeeSalaryPayments.objects.filter(employee=employee).aggregate(Sum('paid'))
        total_paid = payments_sum['paid__sum'] if payments_sum['paid__sum'] is not None else 0

        total_sales_summa = WarehouseSaleProduct.objects.filter(employee=employee).aggregate(Sum('summa'))
        total_salary = total_sales_summa['summa__sum'] if total_sales_summa['summa__sum'] is not None else 0
        try:
            total_salary = total_salary / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']
        except:
            total_salary = 0

        try:
            total_coupon = total_salary // rv_ball['BALL']
        except:
            total_coupon = 0

        return Response({"employee": employee_ser, "total_paid": round(total_paid, 2), "total_salary": round(total_salary, 2), "fee": round(total_coupon, 2), "salary_payments": payments_ser})


class EmployeeGetSalary(APIView): # RetrieveAPIView
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


    def get(self, request, *args, **kwargs):
        employee_user = Employee.objects.filter(id=kwargs['pk'])
        if employee_user:
            employee = employee_user[0]
        else:
            employee = get_object_or_404(Employee, user=get_object_or_404(User, id=kwargs['pk']))

        employee_ser = insteadGetEmployeeInfoSerializer(employee)
        date = kwargs['date']
        # sales_summa = WarehouseSaleProduct.objects.filter(employee=employee, dateTime__startswith=date).aggregate(Sum('summa'))
        sales_summa = WarehouseSaleProduct.objects.filter(employee=employee).aggregate(Sum('summa'))

        employee_sum = sales_summa['summa__sum'] if sales_summa['summa__sum'] is not None else 0
        employee_sum = employee_sum / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']

        # paid = EmployeeSalaryPayments.objects.filter(employee=employee, date__startswith=date).aggregate(Sum('paid'))
        paid = EmployeeSalaryPayments.objects.filter(employee=employee).aggregate(Sum('paid'))
        paid_summa = paid['paid__sum'] if paid['paid__sum'] is not None else 0

        payments_sum = EmployeeSalaryPayments.objects.filter(employee=employee).aggregate(Sum('paid'))
        total_paid = payments_sum['paid__sum'] if payments_sum['paid__sum'] is not None else 0

        total_sales_summa = WarehouseSaleProduct.objects.filter(employee=employee).aggregate(Sum('summa'))
        total_salary = total_sales_summa['summa__sum'] if total_sales_summa['summa__sum'] is not None else 0
        total_salary = total_salary / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']

        return Response({"employee": employee_ser, "salary": round(employee_sum - paid_summa, 2), "paid": paid_summa, "forMonth": str(date)[:7], "fee": round(total_salary - total_paid, 2), "sales_summa": sales_summa['summa__sum']})


class EmployeeGetSalaryFRBot(APIView):  # RetrieveAPIView
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get(self, request, *args, **kwargs):
        employee_user = Employee.objects.filter(id=kwargs['pk'])
        if employee_user:
            employee = employee_user[0]
        else:
            employee = get_object_or_404(Employee, user=get_object_or_404(User, id=kwargs['pk']))

        employee_ser = insteadGetEmployeeInfoSerializer(employee)
        date = str(kwargs['date'])[:7]
        sales_summa = WarehouseSaleProduct.objects.filter(employee=employee, dateTime__startswith=date).aggregate(Sum('summa'))
        # sales_summa = WarehouseSaleProduct.objects.filter(employee=employee).aggregate(Sum('summa'))

        employee_sum = sales_summa['summa__sum'] if sales_summa['summa__sum'] is not None else 0
        employee_sum = employee_sum / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']

        paid = EmployeeSalaryPayments.objects.filter(employee=employee, date__startswith=date).aggregate(Sum('paid'))
        # paid = EmployeeSalaryPayments.objects.filter(employee=employee).aggregate(Sum('paid'))
        paid_summa = paid['paid__sum'] if paid['paid__sum'] is not None else 0

        payments_sum = EmployeeSalaryPayments.objects.filter(employee=employee).aggregate(Sum('paid'))
        total_paid = payments_sum['paid__sum'] if payments_sum['paid__sum'] is not None else 0

        total_sales_summa = WarehouseSaleProduct.objects.filter(employee=employee).aggregate(Sum('summa'))
        total_salary = total_sales_summa['summa__sum'] if total_sales_summa['summa__sum'] is not None else 0
        total_salary = total_salary / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']

        return Response({"employee": employee_ser, "salary": round(employee_sum - paid_summa, 2), "paid": paid_summa, "forMonth": str(date)[:7], "fee": round(total_salary - total_paid, 2), "sales_summa": sales_summa['summa__sum']})


class EmployeeSalaryPaymentListCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = EmployeeSalaryPayments.objects.all()
    serializer_class = EmployeeSalarySerializer

    def create(self, request, *args, **kwargs):
        ser = PostEmployeeSalarySerializer(data=request.data)
        if ser.is_valid():
            employee = Employee.objects.filter(id=ser.validated_data['employee'])
            if employee:
                employee_user = employee[0]
            else:
                employee_user = get_object_or_404(Employee, user=get_object_or_404(User, id=request.data.get("employee")))
            payment = EmployeeSalaryPayments.objects.create(
                employee=employee_user,
                paid=int(request.data.get("paid")),
                date=str(request.data.get("date"))+"-10"
            )
            payment = EmployeeSalarySerializer(payment).data
            # ser.save()
            return Response(payment)
        else:
            return Response(ser.errors)


class EmployeeSalaryPaymentGetDelete(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = EmployeeSalaryPayments.objects.all()
    serializer_class = EmployeeSalarySerializer


class EmployeeSalaryPaymentGetPayments(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, user_id=kwargs['pk'])
        payments = EmployeeSalaryPayments.objects.filter(employee=employee)
        payments_ser = EmployeeSalarySerializer(payments, many=True).data

        return Response({
            "payments": payments_ser
        })

class OwnEmployeeSalaryPaymentGetPayments(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    # queryset = Employee.objects.all()
    # serializer_class = EmployeeSerializer

    def get(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, user=request.user)
        payments = EmployeeSalaryPayments.objects.filter(employee=employee)
        payments_ser = EmployeeSalarySerializer(payments, many=True).data

        return Response({
            "payments": payments_ser
        })


class EmployeeUsersGetSales(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['pk'])
        sales = WarehouseSaleProduct.objects.filter(user=user)
        sales_ser = WarehouseSaleProductSerializer(sales, many=True).data

        return Response({
            "sales": sales_ser
        })




class EmployeeMainPageAPI(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]


    def get(self, request):
        employee = get_object_or_404(Employee, user=request.user)

        header_infos = head_info(request)

        income_products = WarehouseProduct.objects.filter(warehouse=employee.warehouse).aggregate(Sum('amount'))
        income_products_amount = income_products['amount__sum'] if income_products['amount__sum'] is not None else 0
        sale_products = WarehouseSaleProduct.objects.filter(warehouse=employee.warehouse).aggregate(Sum('amount'))
        sale_products_amount = sale_products['amount__sum'] if sale_products['amount__sum'] is not None else 0

        residual_products_amount = income_products_amount - sale_products_amount

        orders = ProductOrder.objects.filter(warehouse=employee.warehouse, done=False)
        orders_ser = ProductOrderSerializer(orders, many=True).data

        header_infos.update({
            "residual_products_amount": residual_products_amount,
            "orders": orders_ser
        })

        return Response(header_infos)


class EmployeeProductPage(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]


    def get(self, request):
        header_infos = head_info(request)
        employee = get_object_or_404(Employee, user=request.user)

        # warehouse_products_history = WarehouseProduct.objects.filter(warehouse=employee.warehouse, dateTime__startswith=month)
        # warehouse_products_history_ser = WarehouseProductSerializer(warehouse_products_history, many=True).data

        sales_history = WarehouseSaleProduct.objects.filter(warehouse=employee.warehouse)
        sales_history_ser = WarehouseSaleProductSerializer(sales_history, many=True).data

        month_product_sales_data = {}
        products_data = Product.objects.all()
        products_data_ser = ProductSerializer(products_data, many=True).data
        month_product_sales = WarehouseSaleProduct.objects.filter(warehouse=employee.warehouse).aggregate(Sum('amount'))
        product_sale_amount_divide = month_product_sales['amount__sum'] if month_product_sales['amount__sum'] is not None else 1

        for product in products_data_ser:
            product_sale_amount = WarehouseSaleProduct.objects.filter(product=product['id'], warehouse=employee.warehouse).aggregate(Sum('amount'))
            product_sale_amount = product_sale_amount['amount__sum'] if product_sale_amount['amount__sum'] is not None else 0
            product_sale_summa = WarehouseSaleProduct.objects.filter(product=product['id'], warehouse=employee.warehouse).aggregate(Sum('summa'))
            product_sale_summa = product_sale_summa['summa__sum'] if product_sale_summa['summa__sum'] is not None else 0

            month_product_sales_data[f"{product['name']}"] = {"product_sales_percent": round(product_sale_amount / product_sale_amount_divide * 100, 1), 'product_sale_amount': product_sale_amount, 'product_sale_summa': product_sale_summa}


        header_infos.update({
            "sales_history": sales_history_ser,
            "month_product_sales_data": month_product_sales_data
        })

        return Response(header_infos)



class EmployeeWarehousePage(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        employee = get_object_or_404(Employee, user=request.user)

        warehouse_products_history = WarehouseProduct.objects.filter(warehouse=employee.warehouse)
        warehouse_products_history_ser = WarehouseProductSerializer(warehouse_products_history, many=True).data

        products_data = Product.objects.all()
        products_data_ser = ProductSerializer(products_data, many=True).data

        warehouse_products_info = []

        for product in products_data_ser:
            income_product = WarehouseProduct.objects.filter(warehouse=employee.warehouse, product__id=product['id']).aggregate(Sum('amount'))
            income_product_sum = income_product['amount__sum'] if income_product['amount__sum'] is not None else 0

            summa_product = WarehouseProduct.objects.filter(warehouse=employee.warehouse, product__id=product['id']).aggregate(Sum('summa'))
            summa_product_sum = summa_product['summa__sum'] if summa_product['summa__sum'] is not None else 0

            paid_product = WarehouseProduct.objects.filter(warehouse=employee.warehouse, product__id=product['id']).aggregate(Sum('paid'))
            paid_product_sum = paid_product['paid__sum'] if paid_product['paid__sum'] is not None else 0

            sales_product = WarehouseSaleProduct.objects.filter(warehouse=employee.warehouse, product__id=product['id']).aggregate(Sum('amount'))
            sales_product_sum = sales_product['amount__sum'] if sales_product['amount__sum'] is not None else 0

            warehouse_products_info.append({
                "product_name": product['name'],
                "amount": income_product_sum - sales_product_sum,
                "debt": summa_product_sum - paid_product_sum,
                "summa": summa_product_sum
            })


        return Response({
            "products": products_data_ser,
            "warehouse_products_info": warehouse_products_info,
            "products_history": warehouse_products_history_ser,
        })


def head_info_by_month(request, month):
    warehouse_income = WarehouseSaleProduct.objects.filter(employee__user=request.user, dateTime__startswith=str(month)[:7]).aggregate(Sum('summa'))
    warehouss_income_sum = warehouse_income['summa__sum'] if warehouse_income['summa__sum'] is not None else 0
    total_users = User.objects.all().count()
    all_coupon = warehouss_income_sum // rv_ball['BALL']

    return {
        "total_sales_summa": warehouss_income_sum,
        "total_users": total_users,
        "total_coupon": all_coupon,
    }


class EmployeeUsersPage(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]


    def get(self, request, *args, **kwargs):
        header_infos = head_info_by_month(request, kwargs['month'])
        from users.calculations import users_all_bonuses_test
        # tree = []
        # m = get_month_info(year_month=str(kwargs['month'])[:7])
        # users = User.objects.filter(deleted=False, date__lte=m).order_by("last_name")
        # for user in users:
        #     salary = user_all_bonuses_test(user_id=user.id, date=str(kwargs['month'])[:7])
        #     tree.append(salary)
        tree = users_all_bonuses_test(date=str(kwargs['month'])[:7])

        header_infos.update(
            {"user_tree": tree}
        )
        return Response(header_infos)



class EmployeeUserTreeGetInfo(APIView):
    permission_classes = [IsAuthenticated, IsEmployee, ]

    def get(self, request, *args, **kwargs):
        get_object_or_404(User, id=kwargs['pk'])
        user = user_all_bonuses_test(user_id=kwargs['pk'], date=str(kwargs['month'])[:7])

        tree = get_all_shajara(user_id=kwargs['pk'], month=f"{str(kwargs['month'])[:7]}-04 10:34:04.860226")

        return Response(
            {
                "user": user,
                "user_tree": tree,
            }
        )


class EmployeeStatisticsPage(APIView):
    permission_classes = [IsAuthenticated, IsEmployee, ]

    def get(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, user=request.user)

        header_infos = head_info(request)

        salary_paid = UsersSalaryPayment.objects.filter(salary_payer=employee.warehouse, paymentDate__startswith=kwargs['month'])
        salary_paid_ser = UsersSalarySerializer(salary_paid, many=True).data

        sales_history = WarehouseSaleProduct.objects.filter(warehouse=employee.warehouse, dateTime__startswith=kwargs['month'])
        sales_history_ser = WarehouseSaleProductSerializer(sales_history, many=True).data

        header_infos.update({
            "paid_users_salary": salary_paid_ser,
            "sales_data": sales_history_ser,
        })

        return Response(header_infos)


class EmployeeOrdersPage(APIView):
    permission_classes = [IsAuthenticated, IsEmployee, ]

    def get(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, user=request.user)

        orders = ProductOrder.objects.filter(warehouse=employee.warehouse, done=False)
        orders_ser = ProductOrderSerializer(orders, many=True).data

        return Response({
            "orders": orders_ser
        })





class EmployeeProductGet(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    queryset = Product.objects.filter(deleted=False)
    serializer_class = ProductSerializer


class EmployeeProfilePage(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        employee = get_object_or_404(Employee, user=request.user)
        employee = insteadGetEmployeeInfoSerializer(employee)

        total_sales_summa = WarehouseSaleProduct.objects.filter(employee__id=employee['id']).aggregate(Sum('summa'))
        total_salary = total_sales_summa['summa__sum'] if total_sales_summa['summa__sum'] is not None else 1
        total_salary_coupon = total_salary // rv_ball['BALL'] # * (10 / 100) * rv_ball['RV']
        # total_salary = total_salary / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']

        employee["coupon"] = total_salary_coupon
        employee["status"] = "Sotuvchi",

        return Response(employee)

class EmployeeProductDiscountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        total_info = head_info(request)

        # discounts = ProductDiscount.objects.filter(endDate__gte=datetime.today())
        discounts = ProductDiscount.objects.all()
        discounts_Ser = ProductDiscountSerializer(discounts, many=True).data

        discounts_data = []

        for disc in discounts_Ser:
            sold = WarehouseSaleProduct.objects.filter(product__id=disc['product']['id'], dateTime__gte=disc['startDate']).filter(dateTime__lte=disc['endDate']).aggregate(Sum('amount'))
            disc['sold'] = sold['amount__sum'] if sold['amount__sum'] is not None else 0
            discounts_data.append(disc)

        total_info.update({
            "dicounts": discounts_data
        })

        return Response(total_info)



class EmployeeSalesMonthAPI(APIView):
    permission_classes = [IsAuthenticated, IsEmployee, ]

    def get(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, user=request.user)

        products = Product.objects.all()
        payments = EmployeeSalaryPayments.objects.filter(employee=employee, date__startswith=kwargs['month']).aggregate(Sum('paid'))
        payments_paid_sum = payments['paid__sum'] if payments['paid__sum'] is not None else 0

        data = {"sales": [], "total_summa": 0, "paid": payments_paid_sum, "debt": 0}

        for product in products:
            sales_product_amount = WarehouseSaleProduct.objects.filter(employee=employee, dateTime__startswith=kwargs['month'], product=product).aggregate(Sum('amount'))
            sales_product_amount_sum = sales_product_amount['amount__sum'] if sales_product_amount['amount__sum'] is not None else 0

            if sales_product_amount_sum == 0:
                continue

            sales_product_summa = WarehouseSaleProduct.objects.filter(employee=employee, dateTime__startswith=kwargs['month'], product=product).aggregate(Sum('summa'))
            sales_product_summa_sum = sales_product_summa['summa__sum'] if sales_product_summa['summa__sum'] is not None else 0

            data.get('sales').append(
                {
                    "product": product.name,
                    "amount": sales_product_amount_sum,
                    "summa": sales_product_summa_sum,
                }
            )
            data['total_summa'] += sales_product_summa_sum
        try:
            total_salary = data['summa'] / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']
        except:
            total_salary = 0

        data['debt'] = total_salary - payments_paid_sum
        return Response(data)


class EmployeeSaleMiniWarehouse(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def post(self, request):
        employee = get_object_or_404(Employee, user=request.user)
        ser = EmployeeSaleMiniWarehouseSerializer(data=request.data)
        amount = int(request.data.get("amount"))
        product_id = request.data.get("product")
        warehouse = get_object_or_404(Warehouse, id=request.data.get("miniwarehouse"))
        product = get_object_or_404(Product, id=product_id)

        if employee.warehouse.warehouse_type == WAREHOUSE and ser.is_valid():
            product_amount = WarehouseProduct.objects.filter(product__id=product_id, warehouse=employee.warehouse).aggregate(Sum('amount'))
            product_amount_sum = product_amount['amount__sum'] if product_amount['amount__sum'] is not None else 0

            product_sales_amount = WarehouseSaleProduct.objects.filter(product__id=product_id, warehouse=employee.warehouse).aggregate(Sum('amount'))
            product_sales_amount_sum = product_sales_amount['amount__sum'] if product_sales_amount['amount__sum'] is not None else 0

            if product_amount_sum - product_sales_amount_sum >= amount:
                data = WarehouseProduct.objects.create(
                    sender=employee.warehouse,
                    product=product,
                    amount=amount,
                    summa=amount*product.price,
                    paid=amount*product.price,
                    warehouse=warehouse
                )
                data_ser = WarehouseProductSerializer(data).data
                return Response(data_ser)
            return Response({
                "success": True,
                "message": "Ombordagi mahsulot qoldig'i kiritilgan miqdordan kam qolgan.",
                "error": ser.errors,
                "product": {"name": f"{product.name}", "amount": product_amount_sum - product_sales_amount_sum}
            })
        return Response({
            "success": True,
            "message": "Faqatgina filiallar mini do'konlarga savdo qilaoladi holos.",
            "error": ser.errors
        })


def get_employee_user_account_bonuses(user):
    cashback = BonusAccount.objects.filter(user=user, bonus_type=CASHBACK).aggregate(Sum('amount'))
    cashback_sum = cashback['amount__sum'] if cashback['amount__sum'] is not None else 0
    voucher = BonusAccount.objects.filter(user=user, bonus_type=VOUCHER).aggregate(Sum('amount'))
    voucher_sum = voucher['amount__sum'] if voucher['amount__sum'] is not None else 0
    # travel = BonusAccount.objects.filter(user=user, bonus_type=TRAVEL).aggregate(Sum('amount'))
    # travel_sum = travel['amount__sum'] if travel['amount__sum'] is not None else 0
    # umrah = BonusAccount.objects.filter(user=user, bonus_type=UMRAH).aggregate(Sum('amount'))
    # umrah_sum = umrah['amount__sum'] if umrah['amount__sum'] is not None else 0
    # autobonus = BonusAccount.objects.filter(user=user, bonus_type=AUTOBONUS).aggregate(Sum('amount'))
    # autobonus_sum = autobonus['amount__sum'] if autobonus['amount__sum'] is not None else 0

    return {
        CASHBACK: cashback_sum,
        VOUCHER: voucher_sum,
        # TRAVEL: travel_sum,
        # UMRAH: umrah_sum,
        # AUTOBONUS: autobonus_sum
            }


class EmployeeGetUserBonusAccountDataAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee, ]

    def get(self, request, user_id):
        user = get_object_or_404(User, user_id=user_id)
        data = get_employee_user_account_bonuses(user)
        return Response(
            {
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                },
                "bonuses": data,
                "bonus_types": [CASHBACK, VOUCHER]
            }
        )


class EmployeeUseBonusAccountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee, ]

    def post(self, request):
        ser = UseBonusAccountSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        pk = request.data.get('user')
        bonus_type = request.data.get('bonus_type')
        amount = float(request.data.get('amount'))

        bonus_amount = BonusAccount.objects.filter(user__id=pk, bonus_type=bonus_type).aggregate(Sum('amount'))
        bonus_amount_sum = bonus_amount['amount__sum'] if bonus_amount['amount__sum'] is not None else 0

        if amount <= bonus_amount_sum and amount > 0 and bonus_type in (CASHBACK, VOUCHER):
            employee = get_object_or_404(Employee, user=request.user)
            BonusAccount.objects.create(
                bonus_type=bonus_type,
                user=User.objects.get(id=pk),
                status="Maosh sifatida",
                amount=amount-amount*2,
                month=str(datetime.today())[:7],
                comment=f"Maosh ko'rinishida to'lab berildi..",
                payer=employee.warehouse
            )

            return Response(
                {
                    "success": True,
                    "message": "Maosh to'lash muvaffaqiyatli amalga oshirildi."
                }
            )
        return Response(
                {
                    "success": False,
                    "message": "Miqdori noto'g'ri kiritildi."
                }, status=400
            )


class EmployeeUsersBonusAccountsDataAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee, ]

    def get(self, request):
        employee = get_object_or_404(Employee, user=request.user)
        bonuses_history = employee.warehouse.payer.all().order_by('-created_time')
        history_ser = AdminBonusAccountSerializer(bonuses_history, many=True).data

        cashback = employee.warehouse.payer.filter(bonus_type=CASHBACK, amount__lt=0).aggregate(Sum('amount'))
        cashback_sum = cashback['amount__sum'] if cashback['amount__sum'] is not None else 0
        voucher = employee.warehouse.payer.filter(bonus_type=VOUCHER, amount__lt=0).aggregate(Sum('amount'))
        voucher_sum = voucher['amount__sum'] if voucher['amount__sum'] is not None else 0

        return Response(
            {
                "paid_bonuses": int(math.fabs(cashback_sum)) + int(math.fabs(voucher_sum)),
                "history": history_ser
            }
        )


class EmployeeGetUserCashackForSaleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee, ]

    def get(self, request, user_id):
        user = get_object_or_404(User, user_id=user_id)
        data = get_employee_user_account_bonuses(user)
        data.pop(VOUCHER)
        return Response(
            {
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                },
                "bonuses": data,
                "bonus_types": [CASHBACK,]
            }
        )

class EmployeeWarehouseSaleProductFromUserBonusesAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsEmployee]
    queryset = WarehouseSaleProduct.objects.all()
    serializer_class = WarehouseSaleProductSerializer

    def create(self, request, *args, **kwargs):
        ser = PostWarehouseSaleProductSerializer2(data=request.data)
        if ser.is_valid():
            user = get_object_or_404(User, id=ser.data.get("user"))
            data = get_employee_user_account_bonuses(user=user)
            product = get_object_or_404(Product, id=ser.data.get("product"))
            product_ser = ProductSerializer(product).data

            sale_summa = int(ser.data.get("amount")) * product_ser.get("price")
            if data[CASHBACK] >= sale_summa:
                employee = get_object_or_404(Employee, user=request.user)
                warehouse_products = WarehouseProduct.objects.filter(warehouse=employee.warehouse, product=product).aggregate(Sum('amount'))
                warehouse_products_amount = warehouse_products['amount__sum'] if warehouse_products['amount__sum'] is not None else 0
                sold_products = WarehouseSaleProduct.objects.filter(warehouse=employee.warehouse, product=product).aggregate(Sum('amount'))
                sold_products_amount = sold_products['amount__sum'] if sold_products['amount__sum'] is not None else 0

                discounts = ProductDiscount.objects.filter(product=product, endDate__gte=datetime.today(), startDate__lte=datetime.today())
                discount_ser = forLandiingPoductSerializer(discounts, many=True)

                if discount_ser != []:
                    discount_amount = discount_ser[0]["amount"]
                    discount_discount = discount_ser[0]["discount"]
                    s_amount = ser.data.get("amount") // discount_amount * discount_discount
                else:
                    s_amount = ser.data.get("amount")


                if warehouse_products_amount - sold_products_amount - int(ser.data.get("amount")) >= 0:
                    sold = WarehouseSaleProduct.objects.create(
                        warehouse=employee.warehouse,
                        employee=employee,
                        user=user,
                        product=product,
                        amount=s_amount,
                        summa=sale_summa,
                        dateTime=datetime.today()
                    )
                    sold_ser = WarehouseSaleProductSerializer(sold).data
                    BonusAccount.objects.create(
                        user=user,
                        bonus_type=CASHBACK,
                        status="Mahsulot sotib olindi",
                        amount=sale_summa-(sale_summa*2),
                        month=str(datetime.today())[:7],
                        comment=f"Mahsulot sotib olish uchun {CASHBACK}'dan to'landi."
                    )
                    return Response({
                        "success": True,
                        "sale_info": sold_ser
                    })
                else:
                    return Response({
                        "success": False,
                        "message": "Sizning filial omboringizda ushbu mahsulotdan qolmagan !"
                    }, status=400)
            else:
                return Response({
                    "success": False,
                    "message": f"{CASHBACK} miqdori yetarli emas."
                }, status=400)
        else:
            return Response({"detail": ser.errors}, status=400)
