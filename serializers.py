from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
          
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__" 
        read_only_fields = ['user']  # User field read-only banai 
        
        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"  
        
class OrderPlacedSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPlaced
        fields = "__all__"                            
        
