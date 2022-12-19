from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from logistic.models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    # проверка существования продукта с неким title будет осуществляться вручную
    # это сделано для обхода ошибки already_exists в момент валидации create и update в StockSerializer
    title = serializers.CharField(max_length=60)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description']

    def check_product_exists(self, title):
        if self.Meta.model.objects.filter(title=title).exists():
            raise ValidationError(f'Product with title {title} already exists!')

    def create(self, validated_data):
        self.check_product_exists(validated_data.get('title'))
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        self.check_product_exists(validated_data.get('title'))
        return super().update(instance, validated_data)


class StockBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'address']


class ProductPositionSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']
        unique_together = ['stock', 'product']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True, required=False)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        positions = validated_data.pop('positions')
        stock = super().create(validated_data)
        for position_data in positions:
            product, _ = Product.objects.update_or_create(**position_data.pop('product'))
            position = StockProduct.objects.create(**{**position_data, 'stock': stock, 'product': product})
            stock.positions.add(position)
        stock.save()
        return stock

    def update(self, instance, validated_data):
        positions = validated_data.pop('positions')
        stock = super().update(instance, validated_data)
        for position_data in positions:
            product, _ = Product.objects.update_or_create(**position_data.pop('product'))
            position_list = StockProduct.objects.filter(stock=stock, product=product)
            position = position_list[0] if len(position_list) else None
            if position:
                if quantity := position_data.get('quantity'):
                    position.quantity = quantity
                position.price = position_data.get('price')
                position.save()
            else:
                position = StockProduct.objects.create(**{**position_data, 'stock': stock, 'product': product})
                stock.positions.add(position)
        stock.save()
        return stock
