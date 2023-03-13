from django.contrib import admin
from .models import User, UserField

# Register your models here.
admin.site.register(User)
admin.site.register(UserField)
