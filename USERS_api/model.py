from django.db import models

# Create your models here.
class User(models.Model):
    User_id = models.AutoField(primary_key=True) 
    Username = models.CharField(max_length=50,unique=True)
    balance = models.IntegerField()


class StockData(models.Model):
    ticker = models.CharField(max_length=10,unique=True) 
    open_price = models.IntegerField()
    close_price = models.IntegerField()
    high = models.IntegerField()
    low = models.IntegerField()
    volume = models.CharField(max_length=20) 
    timestamp = models.DateTimeField() 


class Transactions_table(models.Model):
    transaction_id = models.AutoField(primary_key=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    ticker = models.ForeignKey(StockData, on_delete=models.CASCADE) 
    transaction_type = models.CharField(max_length=4)  
    transaction_volume = models.IntegerField()
    transaction_price = models.IntegerField()
    timestamp = models.DateTimeField()  
