from django.db import models

from employees.models import Employee
from products.models import Product
from shared.models import BaseModel
from users.models import User

WAREHOUSE, MINIWAREHOUSE = "warehouse", "mini_warehouse"

class Warehouse(BaseModel):
    WAREHOUSE_TYPE = (
        (WAREHOUSE, WAREHOUSE),
        (MINIWAREHOUSE, MINIWAREHOUSE)
    )
    name = models.CharField(max_length=200)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=20, null=True)
    photo = models.FileField(null=True, upload_to="warehouse_photos")
    deleted = models.BooleanField(null=True, default=False)
    about = models.TextField(null=True, default="Rizon kompaniyasi filiali")
    warehouse_type = models.CharField(max_length=31, choices=WAREHOUSE_TYPE, default=WAREHOUSE)

    def __str__(self):
        return f"{self.name} {self.phone}"


class WarehouseProduct(BaseModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.SmallIntegerField()
    summa = models.BigIntegerField()
    paid = models.BigIntegerField(default=0)
    dateTime = models.DateTimeField(auto_created=True, auto_now_add=True)
    # dateTime = models.DateTimeField()
    sender = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="product_sender", null=True, blank=True)

    def __str__(self):
        return f"{self.warehouse} {self.product} {self.amount}"


class WarehouseSaleProduct(BaseModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.SmallIntegerField()
    # summa = models.DecimalField(max_digits=20, decimal_places=2)
    summa = models.BigIntegerField()
    dateTime = models.DateTimeField()
    # prduct_dict = models.JSONField()
    # dateTime = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.product} {self.summa} {self.dateTime}"
        # return f"{self.product} {self.summa}"



# class MyUUIDModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=255)
#
#     def __str__(self):
#         return f"{self.id} - {self.name}"
