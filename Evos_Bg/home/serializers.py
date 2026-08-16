from rest_framework import serializers
from home.models import Category, Product, Feedback, Order, ShopCart

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title_uz', 'title_ru', 'image', 'create_at']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title_uz', 'title_ru', 'description_uz', 'description_ru', 'price', 'image', 'status', 'create_at']

class CategoryDetailSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'title_uz', 'title_ru', 'image', 'create_at', 'product',]

    def get_product(self, obj):
        product = Product.objects.filter(category=obj, status='True')
        return ProductSerializer(product, many=True).data

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['user_id', 'username', 'comment',]

class ShopCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCart
        fields = ['user_id', 'username', 'product', 'quantity', 'total_price',]

class CartSerializer(serializers.ModelSerializer):
    product_title_uz = serializers.CharField(source='product.title_uz', read_only=True)
    product_title_ru = serializers.CharField(source='product.title_ru', read_only=True)
    class Meta:
        model = ShopCart
        fields = ['id','user_id', 'username', 'product_title_uz', 'product_title_ru', 'product', 'quantity', 'total_price',]

class OrderGetSerializer(serializers.ModelSerializer):
    time = serializers.TimeField(format="%H:%M")
    create_at = serializers.DateField(format="%d.%m.%Y")
    product_title_uz = serializers.CharField(source='product.title_uz', read_only=True)
    product_title_ru = serializers.CharField(source='product.title_ru', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'code', 'user_id', 'phone', 'location', 'status', 'product_title_uz', 'product_title_ru', 'full_address_uz', 'full_address_ru', "product_data", 'time', 'create_at']

class OrderPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['product', 'full_address_uz', 'full_address_ru', 'location', 'language', 'phone', 'product_data', 'user_id',]