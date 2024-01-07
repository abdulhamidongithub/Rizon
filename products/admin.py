from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(ProductOrder)
admin.site.register(ProductDiscount)
admin.site.register(ProductComment)