from users.models import User
from django.db import models

from shared.models import BaseModel


class Employee(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_created=True, auto_now_add=True)
    # date = models.DateTimeField()
    deleted = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f"{self.warehouse} {self.user}"


class EmployeeSalaryPayments(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    paid = models.BigIntegerField()
    date = models.DateField(null=True)
    paymentDate = models.DateTimeField(auto_created=True, auto_now_add=True)
    # paymentDate = models.DateTimeField()

    def __str__(self):
        return f"{self.employee} {self.paid} {self.date} {self.paymentDate}"


