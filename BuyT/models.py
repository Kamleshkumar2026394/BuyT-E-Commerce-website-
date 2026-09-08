from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class signup(models.Model):
    Full_Name = models.CharField(max_length=20)
    Email = models.EmailField(max_length=50 , unique = True)
    Phone = models.CharField(max_length=11, unique=True)
    Password = models.CharField(max_length=255)

    def __str__(self):
        return self.Full_Name

from django.db import models

# Category Model
class category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    category_image = models.ImageField(upload_to='products/', max_length=255)

    def __str__(self):
        return self.category_name


# Brand Model
class brand(models.Model):
    brand_name = models.CharField(max_length=100, unique=True)
    brand_image = models.ImageField(upload_to='products/', max_length=255)

    def __str__(self):
        return self.brand_name


# Product Model
class product(models.Model):
    image = models.ImageField(upload_to='products/', max_length=255)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    brand = models.ForeignKey(
        brand,
        on_delete=models.CASCADE,
        related_name='products'
    )

    category = models.ForeignKey(
        category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    stock = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    reviews = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    user = models.ForeignKey(signup,on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.Full_Name


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price * self.quantity
# Create your models here.

class Order(models.Model):

    PAYMENT_METHOD_CHOICES = (
        ("COD", "Cash on Delivery"),
        ("ONLINE", "Online Payment"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("REFUNDED", "Refunded"),
    )

    ORDER_STATUS_CHOICES = (
        ("PLACED", "Placed"),
        ("CONFIRMED", "Confirmed"),
        ("PACKED", "Packed"),
        ("SHIPPED", "Shipped"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    )

    user = models.ForeignKey(
        signup,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )

    order_status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS_CHOICES,
        default="PLACED"
    )

    # Coupon information
    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Shipping information
    shipping_address = models.TextField(
        blank=True,
        null=True
    )

    # Tracking
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # Cancellation
    cancellation_reason = models.TextField(
        blank=True,
        null=True
    )

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user.Full_Name}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} - Order #{self.order.id}"

class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)

    def __str__(self):
        return self.email

class Coupon(models.Model):

    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    valid_from = models.DateTimeField()

    valid_until = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(
        default=1
    )

    used_count = models.PositiveIntegerField(
        default=0
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.code


class OrderTracking(models.Model):

    STATUS_CHOICES= (
        ("PLACED", "Placed"),
        ("CONFIRMED", "Confirmed"),
        ("PACKED", "Packed"),
        ("SHIPPED", "Shipped"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tracking_history"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES
    )

    message = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.order.id} - {self.status}"


    
class Wishlist(models.Model):
    user = models.ForeignKey(
        signup,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    product = models.ForeignKey(
        product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_wishlist"
            )
        ]

    def __str__(self):
        return f"{self.user.Full_Name} - {self.product.name}"