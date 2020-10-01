from rest_framework import serializers
from main.models import Product, Contractor, StorageItem, Operation


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = '__all__'


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ['username', 'operation', 'dt_created']


class StorageItemSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        result = serializers.ModelSerializer.to_representation(self, instance)
        result['product_title'] = instance.product.title
        return result

    class Meta:
        model = StorageItem
        fields = ['id', 'product', 'product', 'count', 'dt_created', 'dt_updated', 'to_remove']
