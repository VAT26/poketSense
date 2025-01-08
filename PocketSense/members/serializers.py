from rest_framework import serializers
from .models import Friend, Transaction, Spending, SpendingCategory

# Serializer for the Friend model
class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['user', 'friend', 'status']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user', 'friend', 'amount', 'description', 'date']

class SpendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spending
        fields = ['user', 'amount', 'category', 'date']

class SpendingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendingCategory
        fields = '__all__'