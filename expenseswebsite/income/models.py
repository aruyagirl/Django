from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Source(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class Income(models.Model):
    amount = models.FloatField()
    income_date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.description} - ${self.amount}"   
    
    class Meta:
        ordering = ['-income_date']
        verbose_name_plural = 'Income'
        