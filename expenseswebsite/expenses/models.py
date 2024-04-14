from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Category(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta: 
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name
    
class Expense(models.Model):
    amount = models.FloatField()
    expense_date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    
    def __str__(self):
        return f"{self.description} - ${self.amount}"   
    
    class Meta:
        ordering = ['-expense_date']
        


        