# ecommerce/serializers.py
from rest_framework import serializers
from .models import Category, Product, Review, Saved, Order, OrderItem
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'choice']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Nested serializer for user info

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'product']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True) # Nested serializer for category
    # Use SlugRelatedField to write category by its 'choice' field
    category_id = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='choice',
        source='category',
        write_only=True
    )
    
    # Nested field to show review data
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_price', 'description', 
            'product_photo', 'quantity', 'category', 'category_id', 
            'brand', 'features', 'reviews'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='order_items')
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'status', 'created_at', 'items']