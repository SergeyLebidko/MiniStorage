from rest_framework import serializers
from main.models import Product, Contractor, StorageItem, Document, DocumentItem, Operation


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
        result['product_price'] = instance.product.price
        return result

    class Meta:
        model = StorageItem
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        result = serializers.ModelSerializer.to_representation(self, instance)
        result['contractor_title'] = instance.contractor.title
        return result

    class Meta:
        model = Document
        fields = '__all__'


class DocumentItemSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        result = serializers.ModelSerializer.to_representation(self, instance)
        result['product_title'] = instance.product.title
        result['product_price'] = instance.product.price
        return result

    class Meta:
        model = DocumentItem
        fields = '__all__'
