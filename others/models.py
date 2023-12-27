from django.core.validators import MinValueValidator
from django.db import models

from shared.models import BaseModel


class Promotion(BaseModel):
    name = models.CharField(max_length=255)
    coupon = models.BigIntegerField(validators=[MinValueValidator(0)])
    photo = models.FileField(upload_to="promotions")
    pause = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class PromotionAmount(BaseModel):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    dateTime = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return f"{self.promotion} {self.amount}"

class SalePromotion(BaseModel):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(0)])
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    coupon = models.BigIntegerField(validators=[MinValueValidator(0)])
    dateTime = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return f"{self.promotion} {self.user}"


class BaseParametr(BaseModel):
    bonus_account_lifetime_month = models.IntegerField()
    bonus_account_lifetime_month_break = models.IntegerField()

    def __str__(self): return f"Life Time - {self.bonus_account_lifetime_month} oy | Break Time - {self.bonus_account_lifetime_month_break}"