# serializers.py
from django.contrib.auth.models import User
from django.db.models import Avg
from rest_framework import serializers

from .models import Category, Order, OrderItem, Product, Review, Saved


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "choice"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "product_price",
            "product_image",
            "product_description",
            "category",
            "avg_rating",
            "review_count",
            "is_saved",
        ]

    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(Avg("rating"))["rating__avg"]
        return round(avg, 1) if avg else 0

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Saved.objects.filter(user=request.user, product=obj).exists()
        return False


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "created_at"]


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "total_amount",
            "status",
            "payment_id",
            "created_at",
            "items",
        ]


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_image = serializers.URLField()
    quantity = serializers.IntegerField()
    item_total = serializers.DecimalField(max_digits=10, decimal_places=2)


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_items = serializers.IntegerField()
