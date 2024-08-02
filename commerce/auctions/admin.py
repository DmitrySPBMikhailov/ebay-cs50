from django.contrib import admin
from .models import *


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Listing)
admin.site.register(WatchList)
admin.site.register(Bid)
admin.site.register(Comment)
