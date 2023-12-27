from users.models import User
from django.db import models

from products.models import Product
from shared.models import BaseModel


class Medic(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100, null=True)
    university = models.CharField(max_length=100, null=True)
    bio = models.TextField(null=True)
    share_of_sales_percent = models.SmallIntegerField(null=True, default=4)
    date = models.DateTimeField(auto_created=True, auto_now_add=True)
    # date = models.DateTimeField()
    deleted = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f"{self.user}"


class MedProduct(BaseModel):
    medic = models.ForeignKey(Medic, on_delete=models.CASCADE)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    bonus = models.SmallIntegerField(default=4)
    # date = models.DateField()
    date = models.DateTimeField(auto_created=True, auto_now_add=True)
    # date = models.DateTimeField()
    deleted = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f"{self.medic} {self.product} {self.bonus}%"


class MedSalaryPayment(BaseModel):
    medic = models.ForeignKey(Medic, on_delete=models.CASCADE)
    paid = models.BigIntegerField()
    date = models.DateField(null=True)
    dateTime = models.DateTimeField(auto_created=True, auto_now_add=True)
    # dateTime = models.DateTimeField()

    def __str__(self):
        return f"{self.medic} {self.paid} {self.dateTime}"
