from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from shared.models import BaseModel
from users.models import User
# from warehouses.models import Warehouse


class Product(BaseModel):
    name = models.CharField(max_length=200)
    price = models.BigIntegerField()
    extraPrice = models.BigIntegerField(null=True)
    about = models.TextField(null=True)
    photo_link = models.FileField(blank=True, null=True, upload_to="product_photos")
    discount = models.SmallIntegerField(null=True)
    date = models.DateTimeField(auto_created=True, auto_now_add=True)
    # date = models.DateTimeField()
    deleted = models.BooleanField(null=True, default=False)
    manufacturer = models.CharField(max_length=255, default="Alkimyogar Pharm")
    expiration_date = models.CharField(max_length=255, default="1 yil")
    product_type = models.CharField(max_length=255, default="sirop")
    rate = models.BigIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5, null=True)


    def __str__(self):
        return f"{self.name} {self.price} {self.discount}"


class ProductOrder(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.CASCADE)
    amount = models.SmallIntegerField()
    date = models.DateTimeField(auto_created=True, auto_now_add=True)
    done = models.BooleanField(default=False)

    def __str__(self): return f"{self.user} {self.product}"


class LandingProductOrder(BaseModel):
    customer = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.CASCADE)
    amount = models.SmallIntegerField()
    date = models.DateTimeField(auto_created=True, auto_now_add=True)
    done = models.BooleanField(default=False)

    def __str__(self): return f"{self.product}"


class ProductComment(BaseModel):
    full_name = models.CharField(max_length=255)
    job = models.CharField(max_length=255, null=True)
    photo = models.FileField(blank=True, upload_to="clients", null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()
    dateTime = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self): return f"{self.full_name} {self.job} {self.dateTime}"


class ProductDiscount(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.SmallIntegerField(validators=[MinValueValidator(1)])
    discount = models.SmallIntegerField(validators=[MinValueValidator(1)])
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()

    def __str__(self): return f"{self.product}"
