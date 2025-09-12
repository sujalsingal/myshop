from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    choice = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.choice


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.CharField(max_length=50)
    product_photo = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name


class Saved(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="saved_by"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="saved_products"
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        indexes = [
            models.Index(fields=["user", "product"]),
        ]
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user.username} saved {self.product.product_name}"


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("product", "user")
        indexes = [
            models.Index(fields=["product", "user"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.product_name}- {self.user.username}({self.rating})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    class Meta:
        unique_together = ("id", "user")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"
