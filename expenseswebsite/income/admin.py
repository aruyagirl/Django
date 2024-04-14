from django.contrib import admin
from .models import Income,Source

# Register your models here.

class IncomeAdmin(admin.ModelAdmin):
    list_display=('amount','description','source','income_date')
    search_fields=('amount','description','source__name','income_date')
    list_per_page=20
    
admin.site.register(Income, IncomeAdmin)
admin.site.register(Source)