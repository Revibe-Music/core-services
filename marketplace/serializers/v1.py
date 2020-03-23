"""
Created: 20 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import serializers

from marketplace.models import Good, Transaction

# -----------------------------------------------------------------------------

class BasicGoodSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Good
        fields = [
            'id',
            'category',
            'name',
            'description',
            'price',
            'discount',
            'publish_date',
            'available',
            'repeating',
        ]


class BasicTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'



class GoodSerializer(serializers.ModelSerializer):

    transactions = BasicTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Good
        fields = [
            'id',
            'category',
            'name',
            'description',
            'price',
            'discount',
            'publish_date',
            'available',
            'repeating',
            'transactions',
        ]


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'

