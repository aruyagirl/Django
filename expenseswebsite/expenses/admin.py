from django.contrib import admin
from .models import Expense, Category

# Register your models here.

class ExpenseAdmin(admin.ModelAdmin):
    list_display=('amount','description','category','expense_date')
    search_fields=('amount','description','category__name','expense_date')
    list_per_page=20
    
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)

