from rest_framework import serializers
from .model import User,StockData,Transactions_table
class User_serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
  
class StockData_serializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = '__all__'      

class Transactions_table_serializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions_table
        fields = '__all__' 