import random
from datetime import datetime
from django.db.models import Sum, Max, Count
from rest_framework.generics import get_object_or_404, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from employees.models import EmployeeSalaryPayments, Employee
from employees.serializers import EmployeeSalarySerializer
from medics.models import Medic, MedProduct, MedSalaryPayment
from medics.serializers import insteadGetMeddicInfoSerializer, MedProductSerializer
from others.models import Promotion, PromotionAmount, SalePromotion, BaseParametr
from others.rv_ball import rv_ball
from others.serializers import PromotionSerializer, PromotionAmountSerializer, PutPromotionSerializer, \
    ActivateArchiveInfosSerializer, ForUpdateUsersRolesSerializer, ChangeUserTreeSerializer, \
    TransferBonusAccountSerializer, UseBonusAccountSerializer, BaseParametrSerializer
from products.models import Product, ProductComment, ProductDiscount
from products.serializers import ProductSerializer, LandingProductSerializer, \
    ProductCommentSerializer, ProductDiscountSerializer, forLandiingPoductSerializer
from users.calculations import get_all_shajara, insteadUserSalarySerializer, \
    create_salary_calculate, update_calculated_salary, user_all_bonuses_test, users_all_bonuses_test
from users.models import User, UsersSalaryPayment, OurTeam, UserSalary, Notification, UserNotification, BRAND_MANAGER, \
    ORDINARY_USER, UsersTree, ADMIN, BonusAccount, CASHBACK, VOUCHER, TRAVEL, UMRAH, AUTOBONUS, DONE
from users.new_mp_test import get_salary_data
from users.serializers import UsersSerializer, UsersSalarySerializer, OurTeamSerializer, NotificationSerializer, ForAdminUsersSerializer, AdminBonusAccountSerializer
from warehouses.models import WarehouseSaleProduct, Warehouse, WarehouseProduct, MINIWAREHOUSE, WAREHOUSE
from warehouses.serializers import WarehouseSaleProductSerializer, WarehouseSerializer, insteadGetEmployeeInfoSerializer2, \
    WarehouseProductSerializer
from shared.utility import months_of_given_year
from rest_framework import generics


def totally_info(month: str):
    total_sales_Summa = WarehouseSaleProduct.objects.filter(dateTime__startswith=month).aggregate(Sum('summa'))
    total_sales_Summa = total_sales_Summa['summa__sum'] if total_sales_Summa['summa__sum'] is not None else 0
    # total_users = User.objects.all().count()
    total_users = WarehouseSaleProduct.objects.filter(dateTime__startswith=month).values('user').annotate(user_count=Count('user'))

    total_coupon = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('coupon'))
    total_coupon_sum = total_coupon['coupon__sum'] if total_coupon['coupon__sum'] is not None else 0
    total_ball = 0

    try:
        total_sales_Summa = total_sales_Summa // rv_ball['BALL']
    except:
        total_sales_Summa = 0

    data = {
        "total_sales_summa": total_sales_Summa,
        "total_users": len(total_users),
        "total_coupon": total_coupon_sum,
        "total_ball": total_ball,
    }
    return data



class AdminMainPageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, month):
        total_info = totally_info(month)
        month_sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=month)
        month_sales_data = {}

        for sale in month_sales:
            sale_ser = WarehouseSaleProductSerializer(sale).data
            if str(sale_ser['dateTime'])[:10] not in month_sales_data.keys():
                month_sales_data[f"{str(sale_ser['dateTime'])[:10]}"] = float(sale_ser['summa'])
            else:
                month_sales_data[f"{str(sale_ser['dateTime'])[:10]}"] += float(sale_ser['summa'])


        month_users = User.objects.filter(date__startswith=month)
        month_users_data = {}

        for user in month_users:
            user_ser = UsersSerializer(user).data
            if str(user_ser['date'])[:10] not in month_users_data.keys():
                month_users_data[f"{str(user_ser['date'])[:10]}"] = 1
            else:
                month_users_data[f"{str(user_ser['date'])[:10]}"] += 1

        month_product_sales_data = {}
        products_data = Product.objects.filter(deleted=False)
        products_data_ser = ProductSerializer(products_data, many=True).data
        month_product_sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=month).aggregate(Sum('amount'))
        product_sale_amount_divide = month_product_sales['amount__sum'] if month_product_sales['amount__sum'] is not None else 1

        for product in products_data_ser:
            product_sale_amount = WarehouseSaleProduct.objects.filter(product=product['id'], dateTime__startswith=month).aggregate(Sum('amount'))
            product_sale_amount = product_sale_amount['amount__sum'] if product_sale_amount['amount__sum'] is not None else 1
            product_sale_summa = WarehouseSaleProduct.objects.filter(product=product['id'], dateTime__startswith=month).aggregate(Sum('summa'))
            product_sale_summa = product_sale_summa['summa__sum'] if product_sale_summa['summa__sum'] is not None else 0

            month_product_sales_data[f"{product['name']}"] = {"product_sales_percent": round(product_sale_amount / product_sale_amount_divide * 100, 1), 'product_sale_amount': product_sale_amount, 'product_sale_summa': product_sale_summa}


        warehouses_data = Warehouse.objects.filter(deleted=False, warehouse_type=WAREHOUSE)
        warehouses_data_ser = WarehouseSerializer(warehouses_data, many=True).data
        salary_payers = {}

        for warehouse in warehouses_data_ser:
            # if warehouse['name'] == "Bosh Filial":
                warehouse_salary_paid = UsersSalaryPayment.objects.filter(paymentDate__startswith=month, salary_payer__id=warehouse['id']).aggregate(Sum('paid'))
                warehouse_salary_paid = warehouse_salary_paid['paid__sum'] if warehouse_salary_paid['paid__sum'] is not None else 0
                salary_payers[f"{warehouse['name']}"] = warehouse_salary_paid
            # else:
            #     salary_payers[f"{warehouse['name']}"] = 0

        total_info.update({
            "month_sales_data": month_sales_data,
            "month_came_users": month_users_data,
            "month_product_sales_data": month_product_sales_data,
            "salary_payer_warehouses": salary_payers,
        })
        return Response(total_info)



class WarehousesPageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, month):
        total_info = totally_info(month)
        sales_summa = WarehouseSaleProduct.objects.filter(dateTime__startswith=month).aggregate(Sum('summa'))
        sales_summa = sales_summa['summa__sum'] if sales_summa['summa__sum'] is not None else 1

        warehouses_data = Warehouse.objects.filter(deleted=False, warehouse_type=WAREHOUSE)
        warehouses_data_ser = WarehouseSerializer(warehouses_data, many=True).data
        warehouses_sales_data = {}

        for warehouse in warehouses_data_ser:
            warehouse_sales_data = WarehouseSaleProduct.objects.filter(dateTime__startswith=month, warehouse__id=warehouse['id']).aggregate(Sum('summa'))
            warehouse_sales_data_sum = warehouse_sales_data['summa__sum'] if warehouse_sales_data['summa__sum'] is not None else 1
            wwarehouse_sales_data = WarehouseSaleProduct.objects.filter(dateTime__startswith=month, warehouse__id=warehouse['id']).aggregate(Sum('amount'))
            warehouse_sales_data_amount = wwarehouse_sales_data['amount__sum'] if wwarehouse_sales_data['amount__sum'] is not None else 0

            warehouses_sales_data[f"{warehouse['name']}"] = {
                "sales_percentage": round(warehouse_sales_data_sum / sales_summa * 100, 1),
                "sales_amount": warehouse_sales_data_amount,
                "warehouse": warehouse,
                "sales_by_date": {}
            }

            warehouse_sales_data_by_date = WarehouseSaleProduct.objects.filter(dateTime__startswith=month, warehouse__id=warehouse['id'])
            warehouse_sales_data_by_date_ser = WarehouseSaleProductSerializer(warehouse_sales_data_by_date, many=True).data
            for sale in warehouse_sales_data_by_date_ser:
                if sale['dateTime'] not in warehouses_sales_data[f"{warehouse['name']}"]['sales_by_date'].keys():
                    warehouses_sales_data[f"{warehouse['name']}"]['sales_by_date'][f"{str(sale['dateTime'])}"] = sale['summa']
                else:
                    warehouses_sales_data[f"{warehouse['name']}"]['sales_by_date'][f"{str(sale['dateTime'])}"] += sale['summa']

        total_info.update({"warehouses": warehouses_sales_data})
        total_info.update({"warehouses_info": warehouses_data_ser})
        return Response(total_info)


class MiniWarehousesPageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, month):
        total_info = totally_info(month)
        sales_summa = WarehouseSaleProduct.objects.filter(dateTime__startswith=month).aggregate(Sum('summa'))
        sales_summa = sales_summa['summa__sum'] if sales_summa['summa__sum'] is not None else 1

        warehouses_data = Warehouse.objects.filter(deleted=False, warehouse_type=MINIWAREHOUSE)
        warehouses_data_ser = WarehouseSerializer(warehouses_data, many=True).data
        warehouses_sales_data = {}

        warehouses_data_ser_data = []

        for warehouse in warehouses_data_ser:
            warehouse_sales_data = WarehouseSaleProduct.objects.filter(dateTime__startswith=month, warehouse__id=warehouse['id']).aggregate(Sum('summa'))
            warehouse_sales_data_sum = warehouse_sales_data['summa__sum'] if warehouse_sales_data['summa__sum'] is not None else 1
            wwarehouse_sales_data = WarehouseSaleProduct.objects.filter(dateTime__startswith=month, warehouse__id=warehouse['id']).aggregate(Sum('amount'))
            warehouse_sales_data_amount = wwarehouse_sales_data['amount__sum'] if wwarehouse_sales_data['amount__sum'] is not None else 0

            try:
                ball = warehouse_sales_data_sum // rv_ball['BALL']
            except:
                ball = 0
            warehouse['ball'] = ball
            warehouses_data_ser_data.append(warehouse)

            warehouses_sales_data[f"{warehouse['name']}"] = {
                "sales_percentage": round(warehouse_sales_data_sum / sales_summa * 100, 1),
                "sales_amount": warehouse_sales_data_amount,
                "warehouse": warehouse,
                "ball": ball,
                "sales_by_date": {}
            }

            warehouse_sales_data_by_date = WarehouseSaleProduct.objects.filter(dateTime__startswith=month, warehouse__id=warehouse['id'])
            warehouse_sales_data_by_date_ser = WarehouseSaleProductSerializer(warehouse_sales_data_by_date, many=True).data
            for sale in warehouse_sales_data_by_date_ser:
                if sale['dateTime'] not in warehouses_sales_data[f"{warehouse['name']}"]['sales_by_date'].keys():
                    warehouses_sales_data[f"{warehouse['name']}"]['sales_by_date'][f"{str(sale['dateTime'])}"] = sale['summa']
                else:
                    warehouses_sales_data[f"{warehouse['name']}"]['sales_by_date'][f"{str(sale['dateTime'])}"] += sale['summa']

        total_info.update({"warehouses": warehouses_sales_data})
        total_info.update({"warehouses_info": warehouses_data_ser_data})
        return Response(total_info)



class WarehouseGetAllInfo(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = Warehouse.objects.filter(deleted=False)

    def get(self, request, *args, **kwargs):
        warehouse = get_object_or_404(Warehouse, id=kwargs['pk'])
        warehouse_Ser = WarehouseSerializer(warehouse).data

        warehouses_data = Warehouse.objects.filter(deleted=False, warehouse_type=WAREHOUSE)
        warehouses_data_ser = WarehouseSerializer(warehouses_data, many=True).data

        warehouse_employees = Employee.objects.filter(warehouse__id=warehouse_Ser['id'], deleted=False)
        warehouse_employees_ser = insteadGetEmployeeInfoSerializer2(warehouse_employees, many=True)
        warehouse_employees_data = []

        for employee in warehouse_employees_ser:
            total_sales_summa = WarehouseSaleProduct.objects.filter(employee__id=employee['id'], dateTime__startswith=kwargs['month']).aggregate(Sum('summa'))
            total_salary = total_sales_summa['summa__sum'] if total_sales_summa['summa__sum'] is not None else 0
            try:
                total_salary_coupon = total_salary / rv_ball['BALL'] # * (10 / 100) * rv_ball['RV']
            except:
                total_salary_coupon = 0
            try:
                total_salary_sum = total_salary / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']
            except:
                total_salary_sum = 0
            warehouse_employees_data.append({
                "coupon": total_salary_coupon,
                "total_salary": round(total_salary_sum, 2),
                "status": "Sotuvchi",
                "employee": employee
            })

        warehouse_sales = WarehouseSaleProduct.objects.filter(warehouse=warehouse_Ser['id'], dateTime__startswith=kwargs['month']).aggregate(Sum('summa'))
        warehouse_sales_summa = warehouse_sales['summa__sum'] if warehouse_sales['summa__sum'] is not None else 1

        warehouse_product_sale_amount = WarehouseSaleProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('amount'))
        warehouse_product_sale_amount_count = warehouse_product_sale_amount['amount__sum'] if warehouse_product_sale_amount['amount__sum'] is not None else 0

        warehouse_product_came_amount = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('amount'))
        warehouse_product_came_amount_count = warehouse_product_came_amount['amount__sum'] if warehouse_product_came_amount['amount__sum'] is not None else 0

        warehouse_product_came_summa = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('summa'))
        warehouse_product_came_summa_count = warehouse_product_came_summa['summa__sum'] if warehouse_product_came_summa['summa__sum'] is not None else 0

        warehouse_product_paid_summa = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('paid'))
        warehouse_product_paid_summa_count = warehouse_product_paid_summa['paid__sum'] if warehouse_product_paid_summa['paid__sum'] is not None else 0

        # warehouse_product_history = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id'])
        # warehouse_product_history_ser = WarehouseProductSerializer(warehouse_product_history, many=True).data
        warehouse_product_history_ser_data = []

        for product in Product.objects.all():
            amount = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id'], product=product).aggregate(Sum('amount'))
            amount_sum = amount['amount__sum'] if amount['amount__sum'] is not None else 0

            if amount_sum != 0:
                paid = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id'], product=product).aggregate(Sum('paid'))
                paid_sum = paid['paid__sum'] if paid['paid__sum'] is not None else 0

                summa = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id'], product=product).aggregate(Sum('summa'))
                summa_sum = summa['summa__sum'] if summa['summa__sum'] is not None else 0

                warehouse_product_history_ser_data.append(
                    {
                        "id": "Ko'rsatilmagan",
                        # "warehouse": {
                        #     "id": "57e06190-7c22-44a0-9b47-2ce314ddd809",
                        #     "name": "Bosh Filial",
                        #     "address": "Farg'ona",
                        #     "phone": "+998950813000",
                        #     "photo": "/media/warehouse_photos/M%C3%BCnster_LVM_B%C3%BCrogeb%C3%A4ude_--_2013_--_5149-51.jpg",
                        #     "about": "Rizon kompaniyasi bosh filiali"
                        # },
                        "product": {
                            "name": f"{product.name}",
                            "price": float(product.price),
                            "extraPrice": float(product.extraPrice),
                            # "about": "ҚАЛАМПИРМУНЧОҚ ГИДРОЛАТИ  \r\n\r\nТаркибидаги фаол ингридиентлар: Қалампирмунчоқ гуллари экстракти, дистилланган сув.\r\n\r\nҚалампирмунчоқ ўзига хос доривор хусусиятларга эга зиравордир. Қалампирмунчоқ дарахтининг гул куртаклари тиббиётда ва косметологияда кенг қўлланилади.\r\n\r\n⚠️ Эфир мойларига бой оилага мансуб доим яшил ўсимлик бўлиб,  ўзига хос кучли ҳид ва шифобахш хусусиятларни берадиган бой кимёвий таркибга эга, бу эса танага бебаҳо фойда келтиради.",
                            # "photo_link": "/media/product_photos/photo_2023-06-18_12-36-02_t9qR3rF.jpg",
                            "date": "Umumiy",
                            # "manufacturer": "Alkimyogar Pharm1",
                            # "expiration_date": "1 yil",
                            # "product_type": "sirop"
                        },
                        # "dateTime": "Umumiy",
                        "dateTime": str(datetime.today()),
                        "created_time": "Umumiy",
                        "updated_time": "Umumiy",
                        "amount": amount_sum,
                        "summa": summa_sum,
                        "paid": paid_sum,
                        "debt": summa_sum - paid_sum,
                    }
                )

        month_sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=kwargs['month'], warehouse__id=warehouse_Ser['id'])
        month_sales_ser = WarehouseSaleProductSerializer(month_sales, many=True).data
        month_sales_data = {}

        for sale_ser in month_sales_ser:
            # sale_ser = WarehouseSaleProductSerializer(sale).data
            if str(sale_ser['dateTime'])[:10] not in month_sales_data.keys():
                month_sales_data[f"{str(sale_ser['dateTime'])[:10]}"] = float(sale_ser['summa'])
            else:
                month_sales_data[f"{str(sale_ser['dateTime'])[:10]}"] += float(sale_ser['summa'])

        warehouse_paid_users_salary = UsersSalaryPayment.objects.filter(salary_payer__id=warehouse_Ser['id'], paymentDate__startswith=kwargs['month'])
        warehouse_paid_users_salary_ser = UsersSalarySerializer(warehouse_paid_users_salary, many=True).data
        warehouse_paid_users_salary_data = {}

        for paid in warehouse_paid_users_salary_ser:
            if str(paid['paymentDate'])[:10] not in warehouse_paid_users_salary_data:
                warehouse_paid_users_salary_data[str(paid['paymentDate'])[:10]] = paid['paid']
            else:
                warehouse_paid_users_salary_data[str(paid['paymentDate'])[:10]] += paid['paid']


        warehouse_employee_salary = EmployeeSalaryPayments.objects.filter(paymentDate__startswith=kwargs['month'])
        warehouse_employee_salary_Ser = EmployeeSalarySerializer(warehouse_employee_salary, many=True).data
        warehouse_employee_salary_data = {}

        for paid in warehouse_employee_salary_Ser:

            # total_sales_summa = WarehouseSaleProduct.objects.filter(employee=employee).aggregate(Sum('summa'))
            # total_salary = total_sales_summa['summa__sum'] if total_sales_summa['summa__sum'] is not None else 0
            # total_salary = total_salary / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']

            if str(paid['paymentDate'])[:10] not in warehouse_employee_salary_data:
                warehouse_employee_salary_data[str(paid['paymentDate'])[:10]] = paid['paid']
            else:
                warehouse_employee_salary_data[str(paid['paymentDate'])[:10]] += paid['paid']



        warehouse_product_sales_data = []
        products_data = Product.objects.filter(deleted=False)
        products_data_ser = ProductSerializer(products_data, many=True).data

        for product in products_data_ser:
            warehouse_product_sales = WarehouseSaleProduct.objects.filter(warehouse__id=warehouse_Ser['id'], product__id=product['id']).aggregate(Sum('amount'))
            warehouse_product_sales_amount = warehouse_product_sales['amount__sum'] if warehouse_product_sales['amount__sum'] is not None else 0
            warehouse_product_sales_data.append(
                {
                    "sale_amount": warehouse_product_sales_amount,
                    "product": product
                }
            )

        return Response({
            "warehouse": warehouse_Ser,
            "warehouses_info": warehouses_data_ser,
            "employees": warehouse_employees_data,

            "warehouse_sales_summa": warehouse_sales_summa,
            "product_balance": warehouse_product_came_amount_count - warehouse_product_sale_amount_count,
            "debt": warehouse_product_came_summa_count - warehouse_product_paid_summa_count,

            "warehouse_product_history": warehouse_product_history_ser_data,

            "sale": month_sales_data,
            "paid_users_salary": warehouse_paid_users_salary_data,
            "employee_salary": warehouse_employee_salary_data,
            "product_sales_data": warehouse_product_sales_data,
        })


class MiniWarehouseGetAllInfo(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = Warehouse.objects.filter(deleted=False)

    def get(self, request, *args, **kwargs):
        warehouse = get_object_or_404(Warehouse, id=kwargs['pk'])
        warehouse_Ser = WarehouseSerializer(warehouse).data

        warehouses_data = Warehouse.objects.filter(deleted=False, warehouse_type=MINIWAREHOUSE)
        warehouses_data_ser = WarehouseSerializer(warehouses_data, many=True).data

        warehouse_employees = Employee.objects.filter(warehouse__id=warehouse_Ser['id'], deleted=False)
        warehouse_employees_ser = insteadGetEmployeeInfoSerializer2(warehouse_employees, many=True)
        warehouse_employees_data = []

        for employee in warehouse_employees_ser:
            total_sales_summa = WarehouseSaleProduct.objects.filter(employee__id=employee['id']).aggregate(Sum('summa'))
            total_salary = total_sales_summa['summa__sum'] if total_sales_summa['summa__sum'] is not None else 1
            total_salary_coupon = total_salary / rv_ball['BALL'] # * (10 / 100) * rv_ball['RV']
            # total_salary = total_salary / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']
            warehouse_employees_data.append({
                "coupon": total_salary_coupon,
                # "total_salary": total_salary * 0.1,
                "status": "Sotuvchi",
                "employee": employee
            })

        warehouse_sales = WarehouseSaleProduct.objects.filter(warehouse=warehouse_Ser['id']).aggregate(Sum('summa'))
        warehouse_sales_summa = warehouse_sales['summa__sum'] if warehouse_sales['summa__sum'] is not None else 1

        warehouse_product_sale_amount = WarehouseSaleProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('amount'))
        warehouse_product_sale_amount_count = warehouse_product_sale_amount['amount__sum'] if warehouse_product_sale_amount['amount__sum'] is not None else 0

        warehouse_product_came_amount = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('amount'))
        warehouse_product_came_amount_count = warehouse_product_came_amount['amount__sum'] if warehouse_product_came_amount['amount__sum'] is not None else 0

        warehouse_product_came_summa = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('summa'))
        warehouse_product_came_summa_count = warehouse_product_came_summa['summa__sum'] if warehouse_product_came_summa['summa__sum'] is not None else 0

        warehouse_product_paid_summa = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('paid'))
        warehouse_product_paid_summa_count = warehouse_product_paid_summa['paid__sum'] if warehouse_product_paid_summa['paid__sum'] is not None else 0

        warehouse_product_history = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id'])
        warehouse_product_history_ser = WarehouseProductSerializer(warehouse_product_history, many=True).data


        month_sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=kwargs['month'], warehouse__id=warehouse_Ser['id'])
        month_sales_ser = WarehouseSaleProductSerializer(month_sales, many=True).data
        month_sales_data = {}

        for sale_ser in month_sales_ser:
            # sale_ser = WarehouseSaleProductSerializer(sale).data
            if str(sale_ser['dateTime'])[:10] not in month_sales_data.keys():
                month_sales_data[f"{str(sale_ser['dateTime'])[:10]}"] = float(sale_ser['summa'])
            else:
                month_sales_data[f"{str(sale_ser['dateTime'])[:10]}"] += float(sale_ser['summa'])

        warehouse_paid_users_salary = UsersSalaryPayment.objects.filter(salary_payer__id=warehouse_Ser['id'], paymentDate__startswith=kwargs['month'])
        warehouse_paid_users_salary_ser = UsersSalarySerializer(warehouse_paid_users_salary, many=True).data
        warehouse_paid_users_salary_data = {}

        for paid in warehouse_paid_users_salary_ser:
            if str(paid['paymentDate'])[:10] not in warehouse_paid_users_salary_data:
                warehouse_paid_users_salary_data[str(paid['paymentDate'])[:10]] = paid['paid']
            else:
                warehouse_paid_users_salary_data[str(paid['paymentDate'])[:10]] += paid['paid']


        warehouse_employee_salary = EmployeeSalaryPayments.objects.filter(paymentDate__startswith=kwargs['month'])
        warehouse_employee_salary_Ser = EmployeeSalarySerializer(warehouse_employee_salary, many=True).data
        warehouse_employee_salary_data = {}

        for paid in warehouse_employee_salary_Ser:

            # total_sales_summa = WarehouseSaleProduct.objects.filter(employee=employee).aggregate(Sum('summa'))
            # total_salary = total_sales_summa['summa__sum'] if total_sales_summa['summa__sum'] is not None else 0
            # total_salary = total_salary / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']

            if str(paid['paymentDate'])[:10] not in warehouse_employee_salary_data:
                warehouse_employee_salary_data[str(paid['paymentDate'])[:10]] = paid['paid']
            else:
                warehouse_employee_salary_data[str(paid['paymentDate'])[:10]] += paid['paid']



        warehouse_product_sales_data = []
        products_data = Product.objects.filter(deleted=False)
        products_data_ser = ProductSerializer(products_data, many=True).data

        for product in products_data_ser:
            warehouse_product_sales = WarehouseSaleProduct.objects.filter(warehouse__id=warehouse_Ser['id'], product__id=product['id']).aggregate(Sum('amount'))
            warehouse_product_sales_amount = warehouse_product_sales['amount__sum'] if warehouse_product_sales['amount__sum'] is not None else 0
            warehouse_product_sales_data.append(
                {
                    "sale_amount": warehouse_product_sales_amount,
                    "product": product
                }
            )

        return Response({
            "warehouse": warehouse_Ser,
            "warehouses_info": warehouses_data_ser,
            "employees": warehouse_employees_data,

            "warehouse_sales_summa": warehouse_sales_summa,
            "product_balance": warehouse_product_came_amount_count - warehouse_product_sale_amount_count,
            "debt": warehouse_product_came_summa_count - warehouse_product_paid_summa_count,

            "warehouse_product_history": warehouse_product_history_ser[::-1],

            "sale": month_sales_data,
            "employee_salary": warehouse_employee_salary_data,
            "product_sales_data": warehouse_product_sales_data,
        })


class ProductPageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, reuqest):

        warehouse_product_sales_data = []
        # products_data = Product.objects.filter(deleted=False)
        products_data = Product.objects.order_by("name")
        products_data_ser = ProductSerializer(products_data, many=True).data

        for product in products_data_ser:
            warehouse_product_sales = WarehouseSaleProduct.objects.filter(product=product['id']).aggregate(Sum('amount'))
            warehouse_product_sales_amount = warehouse_product_sales['amount__sum'] if warehouse_product_sales['amount__sum'] is not None else 0
            warehouse_product_sales_data.append(
                {
                    "sale_amount": warehouse_product_sales_amount,
                    "product": product
                }
            )

        product_distribution_data = WarehouseProduct.objects.all().order_by("dateTime")
        product_distribution_data_Ser = WarehouseProductSerializer(product_distribution_data, many=True).data

        return Response({
            "products": products_data_ser,
            "product_sales_data": warehouse_product_sales_data,
            "product_distribution": product_distribution_data_Ser[::-1],
        })


class StatisticPageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, reuqest, month):
        total_info = totally_info(month)
        month_sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=month)
        month_sales_data = {}

        for sale in month_sales:
            sale_ser = WarehouseSaleProductSerializer(sale).data
            if str(sale_ser['dateTime'])[:10] not in month_sales_data.keys():
                month_sales_data[f"{str(sale_ser['dateTime'])[:10]}"] = float(sale_ser['summa'])
            else:
                month_sales_data[f"{str(sale_ser['dateTime'])[:10]}"] += float(sale_ser['summa'])


        month_users = User.objects.filter(date__startswith=month)
        month_users_data = {}

        for user in month_users:
            user_ser = UsersSerializer(user).data
            if str(user_ser['date'])[:10] not in month_users_data.keys():
                month_users_data[f"{str(user_ser['date'])[:10]}"] = 1
            else:
                month_users_data[f"{str(user_ser['date'])[:10]}"] += 1

        month_product_sales_data = {}
        products_data = Product.objects.filter(deleted=False)
        products_data_ser = ProductSerializer(products_data, many=True).data
        month_product_sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=month).aggregate(Sum('amount'))
        product_sale_amount_divide = month_product_sales['amount__sum'] if month_product_sales['amount__sum'] is not None else 1

        for product in products_data_ser:
            product_sale_amount = WarehouseSaleProduct.objects.filter(product=product['id'], dateTime__startswith=month).aggregate(Sum('amount'))
            product_sale_amount = product_sale_amount['amount__sum'] if product_sale_amount['amount__sum'] is not None else 1
            product_sale_summa = WarehouseSaleProduct.objects.filter(product=product['id'], dateTime__startswith=month).aggregate(Sum('summa'))
            product_sale_summa = product_sale_summa['summa__sum'] if product_sale_summa['summa__sum'] is not None else 0

            month_product_sales_data[f"{product['name']}"] = {"product_sales_percent": round(product_sale_amount / product_sale_amount_divide * 100, 1), 'product_sale_amount': product_sale_amount, 'product_sale_summa': product_sale_summa}


        warehouses_data = Warehouse.objects.filter(deleted=False)
        warehouses_data_ser = WarehouseSerializer(warehouses_data, many=True).data
        warehouses_sales_data = []

        for warehouse in warehouses_data_ser:
            warehouse_month_sales = WarehouseSaleProduct.objects.filter(warehouse=warehouse['id'], dateTime__startswith=month)
            warehouse_month_sales_ser = WarehouseSaleProductSerializer(warehouse_month_sales, many=True).data
            warehouse_month_sales_data = {}

            for warehouse_sale in warehouse_month_sales_ser:
                if str(warehouse_sale['dateTime'])[:10] not in warehouse_month_sales_data.keys():
                    warehouse_month_sales_data[f"{str(warehouse_sale['dateTime'])[:10]}"] = float(warehouse_sale['summa'])
                else:
                    warehouse_month_sales_data[f"{str(warehouse_sale['dateTime'])[:10]}"] += float(warehouse_sale['summa'])

            warehouses_sales_data.append(
                {
                    'warehouse': warehouse,
                    "warehouse_sales": warehouse_month_sales_data
                }
            )


        users_salary_payments_data = UsersSalaryPayment.objects.filter(paymentDate__startswith=month)
        users_salary_payments_data_ser = UsersSalarySerializer(users_salary_payments_data, many=True).data
        salary_payments_data = {}

        for payment in users_salary_payments_data_ser:
            if payment['paymentDate'] not in salary_payments_data.keys():
                salary_payments_data[f"{str(payment['paymentDate'])[:10]}"] = payment['paid']
            else:
                salary_payments_data[f"{str(payment['paymentDate'])[:10]}"] += payment['paid']


        total_info.update({
            "month_sales_data": month_sales_data,
            "month_came_users": month_users_data,
            "users_salary": salary_payments_data,
            "month_product_sales_data": month_product_sales_data,
            "warehouses_sales_data": warehouses_sales_data,
        })
        return Response(total_info)


class UsersPageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = (
            'user_id',
            'first_name',
            'last_name',
            'phone_number',
        )
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get(self, request, *args, **kwargs):
        total_info = totally_info(kwargs['month'])
        tree = users_all_bonuses_test(date=str(kwargs['month'])[:7])

        total_info.update(
            {
                "user_tree": tree,
                "users_excel_data": "/media/pdf_files/warehouses_info.xlsx"
            }
        )
        return Response(total_info)



class UserTreeGetInfo(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, *args, **kwargs):
        get_object_or_404(User, id=kwargs['pk'])
        user = user_all_bonuses_test(user_id=kwargs['pk'], date=str(kwargs['month'])[:7])

        tree = get_all_shajara(user_id=kwargs['pk'], month=f"{str(kwargs['month'])[:7]}-04 10:34:04.860226")

        user['coupons'] = 100
        user['total_salary'] = 100

        return Response(
            {
                "user": user,
                "user_tree": tree,
            }
        )

class UserSalesInfo(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        get_object_or_404(User, id=pk)
        sales_history = WarehouseSaleProduct.objects.filter(user__id=pk)
        sales_history = WarehouseSaleProductSerializer(sales_history, many=True).data

        return Response({
            "sales_history": sales_history
        })



class LandingHomeAPI(APIView):

    def get(self, request):
        products = Product.objects.filter(deleted=False)
        products_Ser = LandingProductSerializer(products, many=True).data

        new_products = Product.objects.filter(deleted=False).order_by("date")
        new_products_Ser = LandingProductSerializer(new_products, many=True).data

        product = random.choice(products_Ser)

        rated = Product.objects.filter(rate__gte=3, deleted=False)
        rated_Ser = LandingProductSerializer(rated, many=True).data

        discount_products = ProductDiscount.objects.filter(endDate__gte=datetime.today())
        discount_products_Ser = forLandiingPoductSerializer(discount_products, many=True)

        discounts = []

        for product in discount_products_Ser:
            product['discount'] = f"{product['amount']}+{product['discount']} aksiya"
            discounts.append(product)

        comments = ProductComment.objects.all()
        comments_ser = ProductCommentSerializer(comments, many=True).data

        return Response({
            "product": product,
            "popular": products_Ser,
            "high_rating": rated_Ser,
            "discounts": discounts,
            "new_product": new_products_Ser[:4],
            "comments": comments_ser,
        })


class LandingProductsAPI(APIView):

    def get(self, request):
        products = Product.objects.filter(deleted=False)
        products_Ser = LandingProductSerializer(products, many=True).data

        discount_products = ProductDiscount.objects.filter(endDate__gte=datetime.today())
        discount_products_Ser = forLandiingPoductSerializer(discount_products, many=True)

        product = random.choice(products_Ser)

        discounts = []

        for product in discount_products_Ser:
            product['discount'] = f"{product['amount']}+{product['discount']} aksiya"
            discounts.append(product)

        comments = ProductComment.objects.all()
        comments_ser = ProductCommentSerializer(comments, many=True).data

        return Response({
            "product": product,
            "products": products_Ser,
            "discounts": discounts,
            "comments": comments_ser,
        })


class LandingProductAPI(APIView):

    def get(self, request, pk):
        product = Product.objects.get(id=pk)
        product_Ser = LandingProductSerializer(product).data

        like_products = Product.objects.filter(name__contains=product_Ser['name'])
        like_products_Ser = LandingProductSerializer(like_products, many=True).data

        comments = ProductComment.objects.filter(product=product)
        comments_ser = ProductCommentSerializer(comments, many=True).data

        return Response({
            "product": product_Ser,
            "like_products": like_products_Ser,
            "comments": comments_ser,
        })


class LandingAboutAPI(APIView):

    def get(self, request):
        team = OurTeam.objects.all()
        team_Ser = OurTeamSerializer(team, many=True).data

        return Response({
            "team": team_Ser
        })


class ProductDiscountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        total_info = totally_info("20")

        # discounts = ProductDiscount.objects.filter(endDate__gte=datetime.today())
        discounts = ProductDiscount.objects.all().order_by("-endDate")
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


class AdminPromotionPageAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Promotion.objects.filter(deleted=False)
    serializer_class = PromotionSerializer

    def create(self, request, *args, **kwargs):
        ser = PromotionSerializer(data=request.data)
        if ser.is_valid():
            promotion = Promotion.objects.create(
                name = ser.data.get("name"),
                coupon = ser.data.get("coupon"),
                photo = ser.data.get("photo"),
                pause = ser.data.get("pause"),
            )

            amount = PromotionAmount.objects.create(
                promotion = promotion,
                amount = request.POST.get("amount")
            )

            promotion_Ser = PromotionSerializer(promotion).data
            amount_ser = PromotionAmountSerializer(amount).data
            promotion_Ser['amount'] = amount_ser.get("amount")

            return Response(promotion_Ser)
        else:
            return Response(ser.errors)

    def get(self, request, *args, **kwargs):
        max_coupon = Promotion.objects.aggregate(Max('coupon'))

        step1 = max_coupon['coupon__max'] // 3 if max_coupon['coupon__max'] is not None else 0
        step2 = max_coupon['coupon__max'] // 2 if max_coupon['coupon__max'] is not None else 0

        min_promotions = Promotion.objects.filter(coupon__lte=step1).filter(deleted=False)
        min_promotions_ser = PromotionSerializer(min_promotions, many=True).data

        avg_promotions = Promotion.objects.filter(coupon__gt=step1).filter(coupon__lte=step2).filter(deleted=False)
        avg_promotions_ser = PromotionSerializer(avg_promotions, many=True).data

        max_promotions = Promotion.objects.filter(coupon__gt=step2).filter(deleted=False)
        max_promotions_ser = PromotionSerializer(max_promotions, many=True).data

        min_promotions_ser_data = []
        avg_promotions_ser_data = []
        max_promotions_ser_data = []

        for min_p in min_promotions_ser:
            sold = SalePromotion.objects.filter(promotion__id=min_p['id']).aggregate(Sum('amount'))
            amount = PromotionAmount.objects.filter(promotion__id=min_p['id']).aggregate(Sum('amount'))

            sold = sold['amount__sum'] if sold['amount__sum'] is not None else 0
            amount = amount['amount__sum'] if amount['amount__sum'] is not None else 0

            min_p['amount'] = amount - sold
            min_promotions_ser_data.append(min_p)

        for avg_p in avg_promotions_ser:
            sold = SalePromotion.objects.filter(promotion__id=avg_p['id']).aggregate(Sum('amount'))
            amount = PromotionAmount.objects.filter(promotion__id=avg_p['id']).aggregate(Sum('amount'))

            sold = sold['amount__sum'] if sold['amount__sum'] is not None else 0
            amount = amount['amount__sum'] if amount['amount__sum'] is not None else 0

            avg_p['amount'] = amount - sold
            avg_promotions_ser_data.append(avg_p)

        for max_p in max_promotions_ser:
            sold = SalePromotion.objects.filter(promotion__id=max_p['id']).aggregate(Sum('amount'))
            amount = PromotionAmount.objects.filter(promotion__id=max_p['id']).aggregate(Sum('amount'))

            sold = sold['amount__sum'] if sold['amount__sum'] is not None else 0
            amount = amount['amount__sum'] if amount['amount__sum'] is not None else 0

            max_p['amount'] = amount - sold
            max_promotions_ser_data.append(max_p)


        return Response({
            "small_interval": min_promotions_ser_data,
            "middle_interval": avg_promotions_ser_data,
            "large_interval": max_promotions_ser_data
        })


class AdminPromotionPauseAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Promotion.objects.filter(deleted=False)
    serializer_class = PutPromotionSerializer

    def put(self, request, *args, **kwargs):
        ser = PutPromotionSerializer(data=request.data)
        if ser.is_valid():
            promo = Promotion.objects.get(id=kwargs['pk'])
            promo.pause = ser.data.get("pause")
            promo.save()

            if ser.data.get("pause") == True:
                msg = "Promotion muvaffaqiyatli to'xtatildi !"
            else:
                msg = "Promotion muvaffaqiyatli ochildi !"
            return Response({
                "success": True,
                "message": msg
            })


class AdminPromotionGetUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Promotion.objects.filter(deleted=False)
    serializer_class = PromotionSerializer

    # def get(self, request, **kwargs):
    #     promotion = get_object_or_404(Promotion, id=kwargs['pk'])
    #     promotion_Ser = PromotionSerializer(promotion).data
    #     return Response({
    #         promotion_Ser
    #     })


    def delete(self, request, *args, **kwargs):
        promotion = Promotion.objects.get(id=kwargs['pk'])
        promotion.deleted = True
        promotion.save()

        return Response({
            "success": True,
            "message": "Promotion o'chirildi !"
        })

    # def put(self, request, *args, **kwargs):
    #     ser = PromotionSerializer(data=request.data)
    #     if ser.is_valid():
    #         ser.save()
    #         return Response({
    #             "success": True,
    #             "message": "Promotion muvaffaqiyatli o'zgartirildi !",
    #             "promotion": ser.data
    #         })
    #     else:
    #         return Response(ser.errors)

class PromotionAmountCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    # queryset = PromotionAmount.objects.all()
    # serializer_class = PromotionAmountSerializer

    def post(self, request, *args, **kwargs):
        # ser = PromotionAmountSerializer(data=request.data)
        # if ser.is_valid():
            p_m = PromotionAmount.objects.create(
                promotion=get_object_or_404(Promotion, id=request.data.get("promotion")),
                amount=request.data.get("amount")
            )
            p_m_Ser = PromotionAmountSerializer(p_m).data
            return Response(p_m_Ser)
        # return Response(ser.errors)


class AdminNotificationsAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        ser = NotificationSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            users_data = User.objects.filter(deleted=False)
            for user_data in users_data:
                UserNotification.objects.create(
                    user = user_data,
                    message = request.data.get("message"),
                    title = request.data.get("title")
                )
            return Response(ser.data)
        else:
            return Response(ser.errors)


class UsersSalaryCalculateAPIView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):

        users_data = User.objects.filter(dateOfBirth__startswith=str(datetime.today())[:10])
        for user_data in users_data:
            t = f"Assalomu alaykum Rizon kompaniyasi lideri hurmatli {user_data['first_name']} {user_data['last_name']}\n"
            t += f"Sizni tavallud kuningiz bilan tabriklaymiz! \n"
            t += f"Uzoq umr, sihat-salomatlik hamda oilaviy xotirjamlik tilaymiz! \n"
            t += f"Muvaffaqiyat doimiy hamrohingiz bo’lsin!"
            t += f"\n\nHurmat bilan Rizon Jamoasi 🥳"

            UserNotification.objects.create(
                user=user_data,
                title="Tug'ulgan kuningiz muborak bo'lsin !",
                message=f"{t}",
            )

        month = str(kwargs['month'])+"-01"
        is_there = UserSalary.objects.filter(month__startswith=month)

        # users = User.objects.filter(deleted=False, date__lte=month)
        # users_actives = []
        #
        # for user in users:
        #     if WarehouseSaleProduct.objects.filter(user=user, dateTime__startswith=str(month)[:7]).exists():
        #         users_actives.append(user)

        if list(is_there) == []:
            create_salary_calculate(month=month)
            return Response({
                "success": True,
                "message": "Created salaries",
                # "data": f"{users_actives}"
            })
        else:
            resp = update_calculated_salary(month=month)
            return Response({
                "success": True,
                "message": "Updated salaries",
                # "data": f"{users_actives}",
                "resp": resp
            })


        # notifications = [
        #     {"title": "Notifikatsiya", "message": "Effektiv start bonusi tugashiga 3 kun vaqt qoldi!", "date": datetime.today()},
        #     {"title": "Notifikatsiya", "message": """🥳 Hurmatli Rizon kompaniyasi hamkorlari va guruh a'zolari biz sizlar uchun ajoyib bir yangilikni e'lon qilmoqchimiz.
        #                     😱 Rizon kompaniyasi a'zolari va speaker larimiz kelishgan holda sizlar uchun U-Sin sistemasi va In-Yan ta'limoti bo'yicha BEPUL online dars tashkil qilishga qaror qildi!
        #                     ❓U-Sin sistemasi va In-Yan ta'limoti o'zi nima?
        #                     ♦️Bugungi online darsimizda biz sizlar uchun turkum darslar tashkil qildik bunda siz:
        #                     ✔️ Xitoy tabobati usulida ichki a'zolarni bir biriga bog'liqligini;
        #                     ✔️  Tildan;
        #                     ✔️ Tirnoqdan;
        #                     ✔️ Yuzdagi ajinlardan foydalanib mustaqil ravishda shaxsan o'zingiz tashxis qo'yishni o'rganishingiz mumkin;
        #                     ✅Imkoniyatlardan unumli foydalaning va tibbiy savodxonlikni oshiring!
        #                     😍 Fursatni boy bermang!
        #                     Hoziroq ushbu guruhga qoʻshiling:
        #                     👇👇👇👇👇👇
        #                     @rizonuzguruh
        #
        #                     🎁 Ananalarimizga sodiq qolgan holda faol ishtirokchilarga kutilmagan SOVG'A larimiz bor!
        #
        #                     📆 25.05.2023 soat 20:30""", "date": datetime.today()},
        #                             ]

def finance_page_head_info(month: str):
    totally_income = WarehouseSaleProduct.objects.filter(dateTime__startswith=month).aggregate(Sum('summa'))
    totally_income_sum = totally_income['summa__sum'] if totally_income['summa__sum'] is not None else 0

    totally_salary = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('salary'))
    totally_salary_sum = totally_salary['salary__sum'] if totally_salary['salary__sum'] is not None else 0

    totally_paid = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('paid'))
    totally_paid_sum = totally_paid['paid__sum'] if totally_paid['paid__sum'] is not None else 0

    totally_debt = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('debt'))
    totally_debt_sum = totally_debt['debt__sum'] if totally_debt['debt__sum'] is not None else 0

    totally_coupon = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('coupon'))
    totally_coupon_sum = totally_coupon['coupon__sum'] if totally_coupon['coupon__sum'] is not None else 0

    try:
        employees_total_salary = totally_income_sum / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']
    except:
        employees_total_salary = 0

    employees_payments_sum = EmployeeSalaryPayments.objects.filter(date__startswith=month).aggregate(Sum('paid'))
    employees_total_paid = employees_payments_sum['paid__sum'] if employees_payments_sum['paid__sum'] is not None else 0

    return {
        "total_income": totally_income_sum,
        "total_salary": totally_salary_sum,
        "total_paid": totally_paid_sum,
        "total_debt": totally_debt_sum + employees_total_salary - employees_total_paid,
        "total_coupon": totally_coupon_sum,
        "total_residual": totally_income_sum - totally_paid_sum - employees_total_paid,
        "total_benefit": totally_income_sum - totally_salary_sum - employees_total_salary
    }


def finance_page_users_salary(month: str):
    users_score = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('user_score'))
    users_score_sum = users_score['user_score__sum'] if users_score['user_score__sum'] is not None else 0

    personal_bonus = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('personal_bonus'))
    personal_bonus_sum = personal_bonus['personal_bonus__sum'] if personal_bonus['personal_bonus__sum'] is not None else 0

    forMentorship = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('forMentorship'))
    forMentorship_sum = forMentorship['forMentorship__sum'] if forMentorship['forMentorship__sum'] is not None else 0

    collective_bonus_amount = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('collective_bonus_amount'))
    collective_bonus_amount_sum = collective_bonus_amount['collective_bonus_amount__sum'] if collective_bonus_amount['collective_bonus_amount__sum'] is not None else 0

    extra_bonus = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('extra_bonus'))
    extra_bonus_sum = extra_bonus['extra_bonus__sum'] if extra_bonus['extra_bonus__sum'] is not None else 0

    coupon = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('coupon'))
    coupon_Sum = coupon['coupon__sum'] if coupon['coupon__sum'] is not None else 0

    salary = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('salary'))
    salary_sum = salary['salary__sum'] if salary['salary__sum'] is not None else 0

    debt = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('debt'))
    debt_sum = debt['debt__sum'] if debt['debt__sum'] is not None else 0

    paid = UserSalary.objects.filter(month__startswith=month).aggregate(Sum('paid'))
    paid_sum = paid['paid__sum'] if paid['paid__sum'] is not None else 0

    return {
        "users_score": users_score_sum,
        "personal_bonus": personal_bonus_sum,
        "forMentorship": forMentorship_sum,
        "collective_bonus": collective_bonus_amount_sum,
        "extra_bonus": extra_bonus_sum,
        "coupon": coupon_Sum,
        "salary": salary_sum,
        "debt": debt_sum,
        "paid": paid_sum
    }

def finance_page_employees_salary(month: str):
    employees = []
    total = {"sale": 0, "salary": 0, "paid": 0, "debt": 0}

    employees_data = Employee.objects.filter(deleted=False).order_by("user__last_name")
    employees_data_ser = insteadGetEmployeeInfoSerializer2(employees_data, many=True)
    for employee in employees_data_ser:
        employee_data = {
                        "first_name": employee['first_name'],
                        "last_name": employee['last_name'],
                        "phone_number": employee['phone_number'],
                        "warehouse": employee['warehouse']['name'],
                        "sale": 0,
                        "salary": 0,
                        "paid": 0,
                        "debt": 0
                         }
        sale = WarehouseSaleProduct.objects.filter(employee__id=employee['id'], dateTime__startswith=month).aggregate(Sum('summa'))
        sale_sum = sale['summa__sum'] if sale['summa__sum'] is not None else 0
        try:
            employee_total_salary = round(sale_sum / rv_ball['BALL'] * (10 / 100) * rv_ball['RV'], 2)
        except:
            employee_total_salary = 0

        employee_payments_sum = EmployeeSalaryPayments.objects.filter(date__startswith=month, employee__id=employee['id']).aggregate(Sum('paid'))
        employee_total_paid = employee_payments_sum['paid__sum'] if employee_payments_sum['paid__sum'] is not None else 0

        employee_data['sale'] = sale_sum
        employee_data['salary'] = employee_total_salary
        employee_data['paid'] = employee_total_paid
        employee_data['debt'] = employee_total_salary - employee_total_paid

        total['sale'] += sale_sum
        total['salary'] += employee_total_salary
        total['paid'] += employee_total_paid
        total['debt'] += employee_total_salary - employee_total_paid

        employees.append(employee_data)

    return {
        "employees": employees,
        "total": total,
    }


def finance_page_medic(month: str):
    medics_data = Medic.objects.filter(deleted=False).order_by("user__last_name")
    medics_ser = insteadGetMeddicInfoSerializer(medics_data, many=True)

    medics = []
    total = {"salary": 0, "paid": 0, "debt": 0}

    for medic in medics_ser:
        medic_dict = {
            "first_name": medic['first_name'],
            "last_name": medic['last_name'],
            "phone_number": medic['phone_number'],
            "salary": 0,
            "paid": 0,
            "debt": 0
        }
        med_products = MedProduct.objects.filter(medic__id=medic['id'])
        med_products_ser = MedProductSerializer(med_products, many=True).data

        sales = 0
        for m_p in med_products_ser:
            sale = WarehouseSaleProduct.objects.filter(product__id=m_p["product"]['id'], dateTime__startswith=month).aggregate(Sum('summa'))
            sale_sum = sale['summa__sum'] if sale['summa__sum'] is not None else 0
            try:
                sales += sale_sum / rv_ball['BALL'] * (medic['share_of_sales_percent'] / 100) * rv_ball['RV']
            except:
                sales += 0

        medic_dict['salary'] = round(sales, 2)
        paid = MedSalaryPayment.objects.filter(medic__id=medic['id'], date__startswith=month).aggregate(Sum('paid'))
        medic_dict['paid'] = paid['paid__sum'] if paid['paid__sum'] is not None else 0
        medic_dict['debt'] = medic_dict['salary'] - medic_dict['paid']

        total['salary'] += medic_dict['salary']
        total['paid'] += medic_dict['paid']
        total['debt'] += medic_dict['salary'] - medic_dict['paid']

        medics.append(medic_dict)

    return {
        "medics": medics,
        "total": total
    }

def finance_page_products_sales(month: str):
    products = Product.objects.filter(deleted=False).order_by("name")
    products_ser = ProductSerializer(products, many=True).data

    products_data = []
    for product in products_ser:
        sales = WarehouseSaleProduct.objects.filter(product__id=product['id'], dateTime__startswith=month).aggregate(Sum('summa'))
        sales_sum = sales['summa__sum'] if sales['summa__sum'] is not None else 0

        amount = WarehouseSaleProduct.objects.filter(product__id=product['id'], dateTime__startswith=month).aggregate(Sum('amount'))
        amount_sum = amount['amount__sum'] if amount['amount__sum'] is not None else 0

        products_data.append({"name": product['name'], "amount": amount_sum, "summa": sales_sum})

    return products_data


def get_old_month(month: str):
    from dateutil import relativedelta
    from datetime import date
    lm2 = date(year=int(month[:4]), month=int(month[5:7]), day=1)
    old_month = str(lm2 - relativedelta.relativedelta(months=1))
    return old_month


def finance_page_effective_start_users(month: str):
    old_month = get_old_month(month)  # hozirgi oy oktabr bo'lsa bu avgustni qaytaradi

    users1 = User.objects.filter(date__startswith=str(old_month)[:7], auth_status=DONE)
    users2 = User.objects.filter(date__startswith=str(month)[:7], auth_status=DONE)
    users = users2.union(users1)
    # effective_star_users = [{"users": len(users), "users1": len(users1), "users2": len(users2), "month": month, "old_month": old_month, "users3": []}]
    effective_star_users = []

    for user in users:
        user_salary = UserSalary.objects.filter(month__startswith=str(old_month)[:7], user=user, user_score__gt=0).exclude(user_status="Distributer")
        if user_salary:
            continue
            # user_salary_ser = insteadUserSalarySerializer(user_salary[0], many=False)
            # effective_star_users.append(user_salary_ser)

        else:
            user_salary = UserSalary.objects.filter(month__startswith=str(month)[:7], user=user, user_score__gt=0).exclude(user_status="Distributer")
            if user_salary:
                user_salary_ser = insteadUserSalarySerializer(user_salary[0], many=False)
                effective_star_users.append(user_salary_ser)

    return effective_star_users


def archive_page_products_sales():
    products = Product.objects.filter(deleted=True).order_by("name")
    products_ser = ProductSerializer(products, many=True).data

    products_data = []
    for product in products_ser:
        sales = WarehouseSaleProduct.objects.filter(product__id=product['id']).aggregate(Sum('summa'))
        sales_sum = sales['summa__sum'] if sales['summa__sum'] is not None else 0

        amount = WarehouseSaleProduct.objects.filter(product__id=product['id']).aggregate(Sum('amount'))
        amount_sum = amount['amount__sum'] if amount['amount__sum'] is not None else 0

        product['amount'] = amount_sum
        product['summa'] = sales_sum
        products_data.append(product)

    return products_data


class GetEffectiveStartUsersByMonthApiView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        effective_start_users = finance_page_effective_start_users(month=kwargs['month'])
        return Response(effective_start_users)


# class AdminFinancePageApi(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]
#
#     def get(self, request, **kwargs):
#         finance_page_head = finance_page_head_info(kwargs['month'])
#         finance_page_users = finance_page_users_salary(kwargs['month'])
#         finance_page_employees = finance_page_employees_salary(kwargs['month'])
#         finance_page_medics = finance_page_medic(kwargs['month'])
#         finance_page_products = finance_page_products_sales(kwargs['month'])
#         finance_page_effetive_starts = finance_page_effective_start_users(kwargs['month'])
#
#         if request.user.user_roles == ADMIN:
#             products = Product.objects.filter(deleted=False).order_by("name")
#             products_real_cost = []
#
#             for product in products:
#                 amount = WarehouseSaleProduct.objects.filter(dateTime__startswith=str(kwargs['month'])[:7]).aggregate(Sum('amount'))
#                 amount_sum = amount['amount__sum'] if amount['amount__sum'] is not None else 0
#
#                 product_amount = WarehouseSaleProduct.objects.filter(product=product, dateTime__startswith=str(kwargs['month'])[:7]).aggregate(Sum('amount'))
#                 product_amount_sum = product_amount['amount__sum'] if product_amount['amount__sum'] is not None else 0
#
#                 salary = UserSalary.objects.filter(month__startswith=kwargs['month']).aggregate(Sum('salary'))
#                 salary_sum = salary['salary__sum'] if salary['salary__sum'] is not None else 0
#                 sale_summa = product_amount_sum * product.price
#                 try:
#                     salary_sum = round(salary_sum / amount_sum * product_amount_sum, 2)
#                     real_cost = round((sale_summa - salary_sum) / product_amount_sum, 2)
#                 except:
#                     salary_sum = 0
#                     real_cost = 0
#
#                 p_data = {
#                     "id": product.id,
#                     "name": product.name,
#                     "price": product.price,
#                     # "extraPrice": product.extraPrice,
#                     "sale_amount": product_amount_sum,
#                     "summa": sale_summa,
#                     "salary": salary_sum,
#                     "real_cost": real_cost,
#                 }
#                 products_real_cost.append(p_data)
#
#         else:
#             products_real_cost = []
#
#
#
#         return Response({
#             "head_info": finance_page_head,
#             "users_info": finance_page_users,
#             "employees_info": finance_page_employees,
#             "medics_info": finance_page_medics,
#             "products_info": finance_page_products,
#             "effective_starts_info": finance_page_effetive_starts,
#             "products_real_cost": products_real_cost
#         })


class AdminFinancePageApi(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, **kwargs):
        finance_page_head = finance_page_head_info(kwargs['month'])
        finance_page_users = finance_page_users_salary(kwargs['month'])
        finance_page_employees = finance_page_employees_salary(kwargs['month'])
        finance_page_medics = finance_page_medic(kwargs['month'])
        finance_page_products = finance_page_products_sales(kwargs['month'])
        finance_page_effetive_starts = finance_page_effective_start_users(kwargs['month'])

        if request.user.user_roles == ADMIN:
            products = Product.objects.filter(deleted=False).order_by("name")
            products_real_cost = []

            for product in products:
                product_summa = WarehouseSaleProduct.objects.filter(product=product, dateTime__startswith=str(kwargs['month'])[:7]).aggregate(Sum('summa'))
                product_summa_sum = product_summa['summa__sum'] if product_summa['summa__sum'] is not None else 0

                summa = WarehouseSaleProduct.objects.filter(dateTime__startswith=str(kwargs['month'])[:7]).aggregate(Sum('summa'))
                summa_percent = product_summa_sum / summa['summa__sum'] if summa['summa__sum'] is not None else 0

                product_amount = WarehouseSaleProduct.objects.filter(product=product, dateTime__startswith=str(kwargs['month'])[:7]).aggregate(Sum('amount'))
                product_amount_sum = product_amount['amount__sum'] if product_amount['amount__sum'] is not None else 0

                salary = UserSalary.objects.filter(month__startswith=kwargs['month']).aggregate(Sum('salary'))
                salary_sum = salary['salary__sum'] if salary['salary__sum'] is not None else 0
                salary_sum = salary_sum * summa_percent
                try:
                    real_cost = round((product_summa_sum - salary_sum) / product_amount_sum, 2)
                except:
                    real_cost = 0
                p_data = {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    # "extraPrice": product.extraPrice,
                    "sale_amount": product_amount_sum,
                    "summa": product_summa_sum,
                    "salary": round(salary_sum, 2),
                    "real_cost": real_cost,
                }
                products_real_cost.append(p_data)

        else:
            products_real_cost = []

        return Response({
            "head_info": finance_page_head,
            "users_info": finance_page_users,
            "employees_info": finance_page_employees,
            "medics_info": finance_page_medics,
            "products_info": finance_page_products,
            "effective_starts_info": finance_page_effetive_starts,
            "products_real_cost": products_real_cost
        })


class AdminArchivePageApi(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        warehouses = Warehouse.objects.filter(deleted=True, warehouse_type=WAREHOUSE)
        warehouses_ser = WarehouseSerializer(warehouses, many=True).data

        warehouses_data = []
        for warehouse in warehouses_ser:
            ball = WarehouseSaleProduct.objects.filter(warehouse__id=warehouse['id']).aggregate(Sum('summa'))
            ball_sum = ball['summa__sum'] if ball['summa__sum'] is not None else 0
            warehouse['ball'] = ball_sum // rv_ball['BALL']
            warehouses_data.append(warehouse)


        mini_warehouses = Warehouse.objects.filter(deleted=True, warehouse_type=MINIWAREHOUSE)
        mini_warehouses_ser = WarehouseSerializer(mini_warehouses, many=True).data

        mini_warehouses_data = []
        for mini_warehouse in mini_warehouses_ser:
            ball = WarehouseSaleProduct.objects.filter(warehouse__id=mini_warehouse['id']).aggregate(Sum('summa'))
            ball_sum = ball['summa__sum'] if ball['summa__sum'] is not None else 0
            mini_warehouse['ball'] = ball_sum // rv_ball['BALL']
            mini_warehouses_data.append(mini_warehouse)

        employees = Employee.objects.filter(deleted=True)
        employees_ser = insteadGetEmployeeInfoSerializer2(employees, many=True)

        users = User.objects.filter(deleted=True)
        users_ser = ForAdminUsersSerializer(users, many=True).data

        return Response({
            "warehouses": warehouses_data,
            "employees": employees_ser,
            "products": archive_page_products_sales(),
            "users": users_ser,
            "mini_warehouses": mini_warehouses_data,
        })


class AdminArchiveWarehousePageAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        warehouse = get_object_or_404(Warehouse, id=pk)
        warehouse_ser = WarehouseSerializer(warehouse).data

        employees = Employee.objects.filter(warehouse=warehouse)
        employees_ser = insteadGetEmployeeInfoSerializer2(employees, many=True)

        employees_data = []
        for employee in employees_ser:

            employee_sale = WarehouseSaleProduct.objects.filter(employee__id=employee['id']).aggregate(Sum('summa'))
            employee_sale_sum = employee_sale['summa__sum'] if employee_sale['summa__sum'] is not None else 0
            try:
                employee_ball = employee_sale_sum / rv_ball['BALL']
            except:
                employee_ball = 0

            employee['ball'] = employee_ball

            employees_data.append(employee)

        warehouse_products = WarehouseProduct.objects.filter(warehouse=warehouse)
        warehouse_products_ser = WarehouseProductSerializer(warehouse_products, many=True).data

        sales = WarehouseSaleProduct.objects.filter(warehouse=warehouse)
        sales_ser =WarehouseSaleProductSerializer(sales, many=True).data

        summa = WarehouseSaleProduct.objects.filter(warehouse=warehouse).aggregate(Sum('summa'))
        summa_sum = summa['summa__sum'] if summa['summa__sum'] is not None else 0
        try:
            ball = summa_sum / rv_ball['BALL']
        except:
            ball = 0

        return Response({
            "warehouse": warehouse_ser,
            "employees": employees_data,
            "warehouse_products": warehouse_products_ser,
            "sales": sales_ser,
            "ball": ball,
        })

    def put(self, request, pk):
        ser = ActivateArchiveInfosSerializer(data=request.data)
        if ser.is_valid():
            warehouse = get_object_or_404(Warehouse, id=pk)
            warehouse.deleted = False
            warehouse.save()
            return Response({
                "success": True,
                "message": "Ombor aktivlashtirildi."
            })
        else:
            return Response(ser.errors)


class AdminArchiveEmployeePageAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        employee = get_object_or_404(Employee, id=pk)
        employee_ser = insteadGetEmployeeInfoSerializer2(employee)

        sales = WarehouseSaleProduct.objects.filter(employee=employee)
        sales_ser =WarehouseSaleProductSerializer(sales, many=True).data

        summa = WarehouseSaleProduct.objects.filter(employee=employee).aggregate(Sum('summa'))
        summa_sum = summa['summa__sum'] if summa['summa__sum'] is not None else 0
        try:
            salary = summa_sum / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']
            ball = summa_sum / rv_ball['BALL']
        except:
            salary = 0
            ball = 0

        payments_sum = EmployeeSalaryPayments.objects.filter(employee=employee).aggregate(Sum('paid'))
        total_paid = payments_sum['paid__sum'] if payments_sum['paid__sum'] is not None else 0

        employee_ser["salary"] = salary
        employee_ser["debt"] = salary - total_paid
        employee_ser["paid"] = total_paid
        employee_ser["ball"] = ball

        return Response({
            "employee": employee_ser,
            "sales": sales_ser,
        })

    def put(self, request, pk):
        ser = ActivateArchiveInfosSerializer(data=request.data)
        if ser.is_valid():
            employee = get_object_or_404(Employee, id=pk)
            employee.deleted = False
            employee.save()
            return Response({
                "success": True,
                "message": "Xodim aktivlashtirildi."
            })
        else:
            return Response(ser.errors)

class AdminArchiveProductPageAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        product_ser = ProductSerializer(product).data

        sales = WarehouseSaleProduct.objects.filter(product=product).aggregate(Sum('summa'))
        sales_sum = sales['summa__sum'] if sales['summa__sum'] is not None else 0

        amount = WarehouseSaleProduct.objects.filter(product=product).aggregate(Sum('amount'))
        amount_sum = amount['amount__sum'] if amount['amount__sum'] is not None else 0

        product_ser['amount'] = amount_sum
        product_ser['summa'] = sales_sum
        try:
            ball = sales_sum // rv_ball["BALL"]
        except:
            ball = 0
        product_ser['ball'] = ball

        return Response({
            "product": product_ser
        })

    def put(self, request, pk):
        ser = ActivateArchiveInfosSerializer(data=request.data)
        if ser.is_valid():
            product = get_object_or_404(Product, id=pk)
            product.deleted = False
            product.save()
            return Response({
                "success": True,
                "message": "Mahsulot aktivlashtirildi."
            })
        else:
            return Response(ser.errors)

class AdminArchiveUserInfoPageAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

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

class AdminArchiveUserActivatePageAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def put(self, request, pk):
        ser = ActivateArchiveInfosSerializer(data=request.data)
        if ser.is_valid():
            user = get_object_or_404(User, id=pk)
            user.deleted = False
            user.save()
            return Response({
                "success": True,
                "message": "Mijoz aktivlashtirildi."
            })
        else:
            return Response(ser.errors)

class WarehousesPageInfoAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request):
        warehouses = Warehouse.objects.filter(warehouse_type=WAREHOUSE)
        warehouses_ser = WarehouseSerializer(warehouses, many=True).data
        return Response(warehouses_ser)


class MiniWarehousesPageInfoAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = Warehouse.objects.filter(deleted=False)
    serializer_class = WarehouseSerializer

    def get(self, request, *args, **kwargs):
        warehouses = Warehouse.objects.filter(warehouse_type=MINIWAREHOUSE)
        warehouses_ser = WarehouseSerializer(warehouses, many=True).data
        return Response(warehouses_ser)

    def post(self, request, *args, **kwargs):
        ser = WarehouseSerializer(data=request.data)
        if ser.is_valid():
            w = Warehouse.objects.create(
                name=request.data.get("name"),
                address=request.data.get("address"),
                phone=request.data.get("name"),
                photo=request.data.get("photo"),
                warehouse_type=MINIWAREHOUSE,
                about=request.data.get("about"),
            )
            w_ser = WarehouseSerializer(w).data
            return Response(w_ser)
        return Response(ser.errors)


class WarehousesPageDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def put(self, request, pk):
        ser = ActivateArchiveInfosSerializer(data=request.data)
        if ser.is_valid():
            warehouse = get_object_or_404(Warehouse, id=pk)
            warehouse.deleted = True
            warehouse.save()
            return Response({
                "success": True,
                "message": "Ombor to'xtatildi."
            })
        else:
            return Response(ser.errors)


class AdminChangeUsersRoles(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def put(self, request, pk):
        ser = ForUpdateUsersRolesSerializer(data=request.data)
        if ser.is_valid():
            user = get_object_or_404(User, id=pk)

            if request.data.get("user_role") == "brand_manager":
                user.user_roles = BRAND_MANAGER
            else:
                user.user_roles = ORDINARY_USER

            user.save()
            return Response({
                "success": True,
                "message": "Mijoz roli o'zgardi."
            })

        else:
            return Response(ser.errors)

class AdminChangeUserRole(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def put(self, request):
        ser = ChangeUserTreeSerializer(data=request.data)
        if ser.is_valid():
            UsersTree.objects.filter(invited__user_id=request.data.get("invited")).update(offerer=User.objects.get(user_id=request.data.get("offerer")))
            return Response({
                "success": True,
                "message": "Mijoz ustozi muvaffaqiyatli o'zgartirildi."
            })
        return Response(ser.errors)


class ManagersPageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, month):
        brand_managers = User.objects.filter(user_roles=BRAND_MANAGER, deleted=False)
        # brand_managers_ser = insteadUserSalarySerializer(brand_managers, many=True)
        brand_managers_data = []

        for b_m in brand_managers:
            try:
                user = ForAdminUsersSerializer(b_m).data
                data = UserSalary.objects.get(user=b_m, month__startswith=month)
                user['salary'] = data.salary
                user['paid'] = data.paid
                user['debt'] = data.debt
                brand_managers_data.append(user)
            except:
                pass

        # medics_data = Medic.objects.filter(deleted=False)
        # medics_data_ser = insteadGetMeddicInfoSerializer(medics_data, many=True)
        #
        # medics_full_data = []
        # for medic in medics_data_ser:
        #     medic_products = MedProduct.objects.filter(medic__id=medic['id'], deleted=False)
        #     medic_products_ser = MedProductSerializer(medic_products, many=True).data
        #
        #     med_sum = 0
        #     for product in medic_products_ser:
        #         sales_summa = WarehouseSaleProduct.objects.filter(product=product['product']['id'], dateTime__startswith=month).aggregate(Sum('summa'))
        #
        #         if sales_summa['summa__sum'] is not None:
        #             med_sum += sales_summa['summa__sum'] / rv_ball['BALL'] * (medic['share_of_sales_percent'] / 100) * rv_ball['RV']
        #
        #     med_paid = MedSalaryPayment.objects.filter(medic__id=medic['id'], dateTime__startswith=month).aggregate(Sum('paid'))
        #     med_paid_sum = med_paid['paid__sum'] if med_paid['paid__sum'] is not None else 0
        #
        #     medic["salary"] = round(med_sum - med_paid_sum, 2)
        #     medic["med_products"] = medic_products_ser
        #
        #     medics_full_data.append(medic)

        total_info = totally_info(month)
        total_info.update({
            # "managers": medics_full_data,
            "brand_managers": brand_managers_data
            })

        return Response(total_info)


class EmployeeSalaryPaymentsAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, pk):
        employee = get_object_or_404(Employee, id=pk)
        payments = EmployeeSalaryPayments.objects.filter(employee=employee)
        payments_ser = EmployeeSalarySerializer(payments, many=True).data
        return Response(payments_ser)


class WarehouseSalesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, pk):
        warehouse = get_object_or_404(Warehouse, id=pk)
        warehouse_sales = WarehouseSaleProduct.objects.filter(warehouse=warehouse)
        warehouse_sales_ser = WarehouseSaleProductSerializer(warehouse_sales, many=True).data
        return Response(warehouse_sales_ser)


class SaleDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, pk):
        sale = WarehouseSaleProduct.objects.filter(id=pk).delete()
        return Response({
            "success": True,
            "message": "Sotuv o'chirildi."
        })


def get_user_account_bonuses(user):
    cashback = BonusAccount.objects.filter(user=user, bonus_type=CASHBACK).aggregate(Sum('amount'))
    cashback_sum = cashback['amount__sum'] if cashback['amount__sum'] is not None else 0
    voucher = BonusAccount.objects.filter(user=user, bonus_type=VOUCHER).aggregate(Sum('amount'))
    voucher_sum = voucher['amount__sum'] if voucher['amount__sum'] is not None else 0
    travel = BonusAccount.objects.filter(user=user, bonus_type=TRAVEL).aggregate(Sum('amount'))
    travel_sum = travel['amount__sum'] if travel['amount__sum'] is not None else 0
    umrah = BonusAccount.objects.filter(user=user, bonus_type=UMRAH).aggregate(Sum('amount'))
    umrah_sum = umrah['amount__sum'] if umrah['amount__sum'] is not None else 0
    autobonus = BonusAccount.objects.filter(user=user, bonus_type=AUTOBONUS).aggregate(Sum('amount'))
    autobonus_sum = autobonus['amount__sum'] if autobonus['amount__sum'] is not None else 0

    return {
        CASHBACK: cashback_sum,
        VOUCHER: voucher_sum,
        TRAVEL: travel_sum,
        UMRAH: umrah_sum,
        AUTOBONUS: autobonus_sum
            }


class GetUserBonusAccountDataAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, user_id):
        user = get_object_or_404(User, user_id=user_id)
        data = get_user_account_bonuses(user)
        return Response(
            {
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                },
                "bonuses": data,
                "bonus_types": [CASHBACK, VOUCHER, UMRAH, TRAVEL, AUTOBONUS]
            }
        )


class TransferBonusAccountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def post(self, request):
        ser = TransferBonusAccountSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        pk = request.data.get('user')
        from_bonus_type = request.data.get('from_bonus_type')
        to_bonus_type = request.data.get('to_bonus_type')
        amount = float(request.data.get('amount'))

        bonus_amount = BonusAccount.objects.filter(user__id=pk, bonus_type=from_bonus_type).aggregate(Sum('amount'))
        bonus_amount_sum = bonus_amount['amount__sum'] if bonus_amount['amount__sum'] is not None else 0

        if amount <= bonus_amount_sum and amount > 0:
            BonusAccount.objects.create(
                bonus_type=from_bonus_type,
                user=User.objects.get(id=pk),
                status="Transfer",
                amount=amount-amount*2,
                month=str(datetime.today())[:7],
                comment=f"{from_bonus_type}'dan {to_bonus_type}'ga transfer amalga oshirildi."
            )
            BonusAccount.objects.create(
                bonus_type=to_bonus_type,
                user=User.objects.get(id=pk),
                status="Transfer",
                amount=amount,
                month=str(datetime.today())[:7],
                comment=f"{from_bonus_type}'dan {to_bonus_type}'ga transfer amalga oshirildi."
            )
            return Response(
                {
                    "success": True,
                    "message": "Transfer muvaffaqiyatli amalga oshirildi."
                }
            )
        return Response(
                {
                    "success": False,
                    "message": "Bonus miqdori noto'g'ri kiritildi."
                }, status=400
            )


class UseBonusAccountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def post(self, request):
        ser = UseBonusAccountSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        pk = request.data.get('user')
        bonus_type = request.data.get('bonus_type')
        amount = float(request.data.get('amount'))

        bonus_amount = BonusAccount.objects.filter(user__id=pk, bonus_type=bonus_type).aggregate(Sum('amount'))
        bonus_amount_sum = bonus_amount['amount__sum'] if bonus_amount['amount__sum'] is not None else 0

        if amount <= bonus_amount_sum and amount > 0:
            BonusAccount.objects.create(
                bonus_type=bonus_type,
                user=User.objects.get(id=pk),
                status="Chiqim",
                amount=amount-amount*2,
                month=str(datetime.today())[:7],
                comment=f"Chiqim amalga oshirildi."
            )

            return Response(
                {
                    "success": True,
                    "message": "Chiqim muvaffaqiyatli amalga oshirildi."
                }
            )
        return Response(
                {
                    "success": False,
                    "message": "Chiqim miqdori noto'g'ri kiritildi."
                }, status=400
            )


class AdminUsersBonusAccountsDataAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request):
        bonuses_history = BonusAccount.objects.all().order_by('-created_time')
        history_ser = AdminBonusAccountSerializer(bonuses_history, many=True).data

        cashback = BonusAccount.objects.filter(bonus_type=CASHBACK).aggregate(Sum('amount'))
        cashback_sum = cashback['amount__sum'] if cashback['amount__sum'] is not None else 0
        voucher = BonusAccount.objects.filter(bonus_type=VOUCHER).aggregate(Sum('amount'))
        voucher_sum = voucher['amount__sum'] if voucher['amount__sum'] is not None else 0
        travel = BonusAccount.objects.filter(bonus_type=TRAVEL).aggregate(Sum('amount'))
        travel_sum = travel['amount__sum'] if travel['amount__sum'] is not None else 0
        umrah = BonusAccount.objects.filter(bonus_type=UMRAH).aggregate(Sum('amount'))
        umrah_sum = umrah['amount__sum'] if umrah['amount__sum'] is not None else 0
        autobonus = BonusAccount.objects.filter(bonus_type=AUTOBONUS).aggregate(Sum('amount'))
        autobonus_sum = autobonus['amount__sum'] if autobonus['amount__sum'] is not None else 0

        return Response(
            {
                CASHBACK: cashback_sum,
                VOUCHER: voucher_sum,
                TRAVEL: travel_sum,
                UMRAH: umrah_sum,
                AUTOBONUS: autobonus_sum,
                "history": history_ser
            }
        )


class AdminParametrsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request):
        bonus_parametr = BaseParametr.objects.first()
        ser_data = BaseParametrSerializer(bonus_parametr).data
        return Response(
            {
                "bonus_parametrs": ser_data
            }
        )

    def post(self, request):
        ser = BaseParametrSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        BaseParametr.objects.all().update(
            bonus_account_lifetime_month=request.data.get('bonus_account_lifetime_month'),
            bonus_account_lifetime_month_break=request.data.get('bonus_account_lifetime_month_break'),
                                          )
        return Response(
            {
                "success": True,
                "message": "Muvaffaqiyatli o'zgartirildi."
            }
        )


class UserNewMPBonusTestAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, user_id, month):
        data = get_salary_data(user_id=user_id, month=month)
        return Response({
            "data": data
        })


def get_user_tree_view(request, user_id, month):
    month = str(month)[:7]
    tree = [[]]
    id = [str(user_id)]
    id_2 = [str(user_id)]

    sanoq = 1
    while len(id) > 0:
        sanoq += 1
        user_tree1 = UsersTree.objects.filter(offerer__user_id=id[0]).filter(deleted=False)

        for follower in user_tree1:
            salary = UserSalary.objects.filter(user=follower.invited, month__startswith=month)
            if len(salary) > 0:
                first_name = salary[0].user.first_name
                last_name = salary[0].user.last_name
                phone_number = salary[0].user.phone_number
                user_score = salary[0].user_score
                user_tree_score = salary[0].user_tree_score
                user_status = salary[0].user_status
            else:
                first_name = follower.invited.first_name
                last_name = follower.invited.last_name
                phone_number = follower.invited.phone_number
                user_score = 0
                user_tree_score = 0
                user_status = "Distributer"
            tree[-1].append(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone_number": phone_number,
                    "user_score": user_score,
                    "user_tree_score": user_tree_score,
                    "user_status": user_status,
                    "user_id": follower.invited.user_id,
                }
            )
            # id.append(str())
            id_2.append(str(follower.invited.user_id))
        id.pop(0)
        if len(id) == 0:
            id = id_2
            id_2 = []
            tree.append([])

    return render(request, "tree_view.html", {"data": {"tree": tree, "month": month}})


class GetLastUsersAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.filter(auth_status=DONE, deleted=False).order_by("-date")
        users_ser = ForAdminUsersSerializer(users, many=True).data
        return Response(users_ser)

##############################################################################################################################################################

class AdminMainPageAPIView2(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, month):
        total_info = totally_info(month)
        months = months_of_given_year(str(month)[:4])

        year_sales_data = {}
        total_sales_summa = 0
        for year_month in months:
            month_sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=year_month).aggregate(Sum('summa'))
            month_sales_summa = month_sales['summa__sum'] if month_sales['summa__sum'] is not None else 0
            year_sales_data[str(year_month)] = month_sales_summa
            total_sales_summa += month_sales_summa
        year_sales_data["Jami"] = total_sales_summa

        month_users_data = {}
        total_users = 0
        for year_month in months:
            month_users = User.objects.filter(date__startswith=year_month).count()
            month_users_data[str(year_month)] = month_users
            total_users += month_users
        month_users_data["Jami"] = total_users

        year_products_sales_data = []
        # products_data = Product.objects.filter(deleted=False)
        products = Product.objects.all().order_by("name")

        for product in products:
            product_data = {
                "Mahsulot": f"{product.name}",
                # "data": []
            }
            total_amount = 0
            for month in months:
                product_sale_amount = WarehouseSaleProduct.objects.filter(product=product, dateTime__startswith=month).aggregate(Sum('amount'))
                product_sold_amount = product_sale_amount['amount__sum'] if product_sale_amount['amount__sum'] is not None else 0
                # product_data['data'].append(
                #     {
                #         "month": month,
                #         "amount": product_sold_amount
                #     }
                # )
                product_data[str(month)] = product_sold_amount
                total_amount += product_sold_amount
            product_data['Jami'] = total_amount
            year_products_sales_data.append(product_data)


        year_warehouses_salary_paid_data = []
        # warehouses = Warehouse.objects.filter(deleted=False)
        warehouses = Warehouse.objects.all().order_by("name")

        for warehouse in warehouses:
            total_amount = 0
            total_paid = {
                "Filial": f"{warehouse.name}",
                # "data": []
            }
            for month in months:
                warehouse_salary_paid = UsersSalaryPayment.objects.filter(paymentDate__startswith=month, salary_payer=warehouse).aggregate(Sum('paid'))
                warehouse_salary_paid = warehouse_salary_paid['paid__sum'] if warehouse_salary_paid['paid__sum'] is not None else 0
                # total_paid['data'].append(
                #     {
                #         "month": month,
                #         "amount": warehouse_salary_paid
                #     }
                # )
                total_paid[str(month)] = warehouse_salary_paid
                total_amount += warehouse_salary_paid
            total_paid['Jami'] = total_amount
            year_warehouses_salary_paid_data.append(total_paid)

        total_info.update({
            "sales_data": year_sales_data,
            "users_statistics": month_users_data,
            "product_sales_data": year_products_sales_data,
            "salary_payer_warehouses": year_warehouses_salary_paid_data,
        })
        return Response(total_info)


class WarehousesPageAPIViewV2(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, month):
        month = str(month)[:4]
        total_info = totally_info(month)
        months = months_of_given_year(str(month)[:4])

        warehouses_data = Warehouse.objects.filter(deleted=False, warehouse_type=WAREHOUSE).order_by("name")
        warehouses_data_ser = WarehouseSerializer(warehouses_data, many=True).data
        warehouses_sales_data = []
        warehouses_sales_data_percentage = []

        for warehouse in warehouses_data:
            data = {
                # "Filial": warehouse.name,
                "Filial": f'<a href="/Branches/{warehouse.id}">{warehouse.name}</a>',
            }
            total = 0
            warehouse_percentage = {
                "Filial": f'<a href="/Branches/{warehouse.id}">{warehouse.name}</a>',
            }
            for month in months:
                sales_summa = WarehouseSaleProduct.objects.filter(dateTime__startswith=month).aggregate(Sum('summa'))
                sales_summa = sales_summa['summa__sum'] if sales_summa['summa__sum'] is not None else 0
                sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=month, warehouse=warehouse).aggregate(Sum('summa'))
                sales_sum = sales['summa__sum'] if sales['summa__sum'] is not None else 0
                data[str(month)] = sales_sum
                total += sales_sum

                try:
                    sales_percentage = round(sales_sum / sales_summa * 100, 1)
                except Exception as e:
                    print(f"{e=}")
                    sales_percentage = 0

                warehouse_percentage[str(month)] = sales_percentage
            warehouses_sales_data_percentage.append(warehouse_percentage)
            data['Jami'] = total
            warehouses_sales_data.append(data)
        total_info.update({"warehouses": warehouses_sales_data})
        total_info.update({"warehouses_percentage": warehouses_sales_data_percentage})
        total_info.update({"warehouses_info": warehouses_data_ser})
        return Response(total_info)


class WarehouseGetAllInfoV2(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]
    queryset = Warehouse.objects.filter(deleted=False)

    def get(self, request, *args, **kwargs):
        warehouse = get_object_or_404(Warehouse, id=kwargs['pk'])
        warehouse_Ser = WarehouseSerializer(warehouse).data
        month = str(kwargs['month'])[:7]
        months = months_of_given_year(str(month)[:4])

        warehouses_data = Warehouse.objects.filter(deleted=False, warehouse_type=WAREHOUSE)
        warehouses_data_ser = WarehouseSerializer(warehouses_data, many=True).data

        warehouse_employees = Employee.objects.filter(warehouse__id=warehouse_Ser['id'], deleted=False)
        warehouse_employees_ser = insteadGetEmployeeInfoSerializer2(warehouse_employees, many=True)
        warehouse_employees_data = []

        for employee in warehouse_employees_ser:
            total_sales_summa = WarehouseSaleProduct.objects.filter(employee__id=employee['id'], dateTime__startswith=kwargs['month']).aggregate(Sum('summa'))
            total_salary = total_sales_summa['summa__sum'] if total_sales_summa['summa__sum'] is not None else 0
            try:
                total_salary_coupon = total_salary / rv_ball['BALL'] # * (10 / 100) * rv_ball['RV']
            except:
                total_salary_coupon = 0
            try:
                total_salary_sum = total_salary / rv_ball['BALL'] * (10 / 100) * rv_ball['RV']
            except:
                total_salary_sum = 0
            warehouse_employees_data.append({
                "coupon": total_salary_coupon,
                "total_salary": round(total_salary_sum, 2),
                "status": "Sotuvchi",
                "employee": employee
            })

        warehouse_sales = WarehouseSaleProduct.objects.filter(warehouse=warehouse_Ser['id'], dateTime__startswith=month).aggregate(Sum('summa'))
        warehouse_sales_summa = warehouse_sales['summa__sum'] if warehouse_sales['summa__sum'] is not None else 1

        warehouse_product_sale_amount = WarehouseSaleProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('amount'))
        warehouse_product_sale_amount_count = warehouse_product_sale_amount['amount__sum'] if warehouse_product_sale_amount['amount__sum'] is not None else 0

        warehouse_product_came_amount = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('amount'))
        warehouse_product_came_amount_count = warehouse_product_came_amount['amount__sum'] if warehouse_product_came_amount['amount__sum'] is not None else 0

        warehouse_product_came_summa = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('summa'))
        warehouse_product_came_summa_count = warehouse_product_came_summa['summa__sum'] if warehouse_product_came_summa['summa__sum'] is not None else 0

        warehouse_product_paid_summa = WarehouseProduct.objects.filter(warehouse__id=warehouse_Ser['id']).aggregate(Sum('paid'))
        warehouse_product_paid_summa_count = warehouse_product_paid_summa['paid__sum'] if warehouse_product_paid_summa['paid__sum'] is not None else 0

        warehouse_product_history_ser_data = []
        products = Product.objects.all().order_by('name')
        for product in products:
            amount = WarehouseProduct.objects.filter(warehouse=warehouse, product=product, dateTime__startswith=month).aggregate(Sum('amount'))
            amount_sum = amount['amount__sum'] if amount['amount__sum'] is not None else 0

            paid = WarehouseProduct.objects.filter(warehouse=warehouse, product=product, dateTime__startswith=month).aggregate(Sum('paid'))
            paid_sum = paid['paid__sum'] if paid['paid__sum'] is not None else 0

            summa = WarehouseProduct.objects.filter(warehouse=warehouse, product=product, dateTime__startswith=month).aggregate(Sum('summa'))
            summa_sum = summa['summa__sum'] if summa['summa__sum'] is not None else 0

            warehouse_product_history_ser_data.append(
                {
                    "Mahsulot": f"{product.name}",
                    "Miqdor": amount_sum,
                    "Summada": summa_sum,
                    "To'landi": paid_sum,
                    "Qarzdorlik": summa_sum - paid_sum,
                }
            )

        year_products_given_data = []
        products = Product.objects.all().order_by("name")

        for product in products:
            product_data = {
                "Mahsulot": f"{product.name}",
            }
            total_amount = 0
            total_summa = 0
            total_paid = 0

            for month in months:
                product_amount = WarehouseProduct.objects.filter(product=product, dateTime__startswith=month).aggregate(Sum('amount'))
                product_amount = product_amount['amount__sum'] if product_amount['amount__sum'] is not None else 0
                product_data[str(month)] = product_amount
                total_amount += product_amount

                product_summa = WarehouseProduct.objects.filter(product=product, dateTime__startswith=month).aggregate(Sum('summa'))
                total_summa += product_summa['summa__sum'] if product_summa['summa__sum'] is not None else 0

                product_summa_paid = WarehouseProduct.objects.filter(product=product, dateTime__startswith=month).aggregate(Sum('paid'))
                total_paid += product_summa_paid['paid__sum'] if product_summa_paid['paid__sum'] is not None else 0

            product_data['Jami Miqdor'] = total_amount
            product_data['Summa'] = total_summa
            product_data["To'landi"] = total_paid
            product_data['Qarzdorlik'] = total_summa - total_paid
            year_products_given_data.append(product_data)

        return Response({
            "warehouse": warehouse_Ser,
            "warehouses_info": warehouses_data_ser,
            "employees": warehouse_employees_data,

            "warehouse_sales_summa": warehouse_sales_summa,
            "product_balance": warehouse_product_came_amount_count - warehouse_product_sale_amount_count,
            "debt": warehouse_product_came_summa_count - warehouse_product_paid_summa_count,

            "warehouse_product_history": warehouse_product_history_ser_data,
            # "product_history_year": year_warehouse_product_history_ser_data,
            "year_products_given_data": year_products_given_data,
        })


class AdminStatisticsPageAPIViewV2(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser, ]

    def get(self, request, month):
        month = str(month)[:7]
        total_info = totally_info(month)
        months = months_of_given_year(str(month)[:4])

        year_sales_data = {}
        total_sales_summa = 0
        for year_month in months:
            month_sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=year_month).aggregate(Sum('summa'))
            month_sales_summa = month_sales['summa__sum'] if month_sales['summa__sum'] is not None else 0
            year_sales_data[str(year_month)] = month_sales_summa
            total_sales_summa += month_sales_summa
        year_sales_data["Jami"] = total_sales_summa

        month_users_data = {}
        total_users = 0
        for year_month in months:
            month_users = User.objects.filter(date__startswith=year_month).count()
            month_users_data[str(year_month)] = month_users
            total_users += month_users
        month_users_data["Jami"] = total_users

        year_products_sales_data = []
        products = Product.objects.all().order_by("name")

        for product in products:
            product_data = {
                "Mahsulot": f"{product.name}",
            }
            total_amount = 0
            for month in months:
                product_sale_amount = WarehouseSaleProduct.objects.filter(product=product, dateTime__startswith=month).aggregate(Sum('amount'))
                product_sold_amount = product_sale_amount['amount__sum'] if product_sale_amount['amount__sum'] is not None else 0
                product_data[str(month)] = product_sold_amount
                total_amount += product_sold_amount
            product_data['Jami'] = total_amount
            year_products_sales_data.append(product_data)

        year_warehouses_salary_paid_data = []
        warehouses = Warehouse.objects.all().order_by("name")

        for warehouse in warehouses:
            total_amount = 0
            total_paid = {
                "Filial": f"{warehouse.name}",
            }
            for month in months:
                warehouse_salary_paid = UsersSalaryPayment.objects.filter(paymentDate__startswith=month, salary_payer=warehouse).aggregate(Sum('paid'))
                warehouse_salary_paid = warehouse_salary_paid['paid__sum'] if warehouse_salary_paid['paid__sum'] is not None else 0
                total_paid[str(month)] = warehouse_salary_paid
                total_amount += warehouse_salary_paid
            total_paid['Jami'] = total_amount
            year_warehouses_salary_paid_data.append(total_paid)

        warehouses_sales_data = []

        for warehouse in warehouses:
            data = {
                "Filial": f'<a href="/Branches/{warehouse.id}">{warehouse.name}</a>',
            }
            total = 0

            for month in months:
                sales = WarehouseSaleProduct.objects.filter(dateTime__startswith=month, warehouse=warehouse).aggregate(Sum('summa'))
                sales_sum = sales['summa__sum'] if sales['summa__sum'] is not None else 0
                data[str(month)] = sales_sum
                total += sales_sum

            data['Jami'] = total
            warehouses_sales_data.append(data)

        total_info.update({
            "sales_data": year_sales_data,
            "users_statistics": month_users_data,
            "product_sales_data": year_products_sales_data,
            "salary_payer_warehouses": year_warehouses_salary_paid_data,
            "warehouses_data": warehouses_sales_data
        })
        return Response(total_info)


class AdminProductDiscountDestroy(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, pk):
        discount = ProductDiscount.objects.filter(id=pk).delete()
        return Response(
            {
                "success": True,
                "message": "Aksiya o'chirildi."
            }
        )


class AdminUsersFilterAPIViewV2(generics.ListAPIView):
    # permission_classes = [IsAuthenticated, IsAdminUser, ]
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = (
            'user_id',
            'first_name',
            'last_name',
        )
    queryset = User.objects.filter(deleted=False, auth_status=DONE)
    serializer_class = ForAdminUsersSerializer
