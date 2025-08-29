from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone  # Add this import
import uuid

from cloudinary.models import CloudinaryField
from decimal import Decimal
from froala_editor.fields import FroalaField
from django.utils.text import slugify

# Helper function for default end date
def default_deal_end_time():
    return timezone.now() + timedelta(hours=24)

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField()
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug_candidate = base_slug
            num = 1
            while Category.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{num}"
                num += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Deals_of_the_Day(models.Model):
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=default_deal_end_time)

    def __str__(self):
        return f"Deal from {self.start_date} to {self.end_date}"

    # Check if deal is active
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    # Remaining time in seconds
    def remaining_seconds(self):
        now = timezone.now()
        remaining = (self.end_date - now).total_seconds()
        return max(int(remaining), 0)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    description_long = FroalaField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_image = CloudinaryField()
    product_id = models.CharField(max_length=12, unique=True, editable=False, blank=True)

    # Tech-specific fields
    brand = models.CharField(max_length=100, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    warranty_months = models.IntegerField(default=12)

    # Deal
    deals_of_the_day = models.ForeignKey(
        Deals_of_the_Day,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    discount_percentage = models.PositiveIntegerField(default=0)

    # Product options
    sizes = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    colors = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    # Stock
    in_stock = models.PositiveIntegerField(default=0)

    # Category
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    keywords = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate unique product_id if not exists
        if not self.product_id:
            while True:
                new_id = 'PROD' + str(uuid.uuid4()).replace('-', '')[:8].upper()
                if not Product.objects.filter(product_id=new_id).exists():
                    self.product_id = new_id
                    break

        # Generate unique slug if not exists
        if not self.slug:
            base_slug = slugify(self.name)
            slug_candidate = base_slug
            num = 1
            while Product.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{num}"
                num += 1
            self.slug = slug_candidate

        super().save(*args, **kwargs)

    # Check if deal is active
    def is_deal_active(self):
        if self.deals_of_the_day:
            return self.deals_of_the_day.is_active()
        return False

    # Remaining time for countdown
    def deal_remaining_seconds(self):
        if self.deals_of_the_day:
            return self.deals_of_the_day.remaining_seconds()
        return 0

    # Calculate final price with discount
    def get_final_price(self):
        if self.is_deal_active() and self.discount_percentage:
            discount_amount = (Decimal(self.discount_percentage) / Decimal(100)) * self.price
            return self.price - discount_amount
        return self.price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    image = CloudinaryField()

    def __str__(self):
        return f"Image for {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),  # ✅ new

    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Product, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='pending')
    payment_staus = models.CharField(max_length=300, choices=PAYMENT_STATUS_CHOICES, default='pending')
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    address = models.TextField()
    zip_code = models.CharField(max_length=20)
    delivery_date = models.DateField(null=True, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)  # ✅ new field to track when payment was made
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)  # ✅ Add this line

    def __str__(self):
        return f"Order #{self.id} for {self.email}"

    def save(self, *args, **kwargs):
        if not self.delivery_date:
            self.delivery_date = timezone.now().date() + timedelta(days=3)
        super().save(*args, **kwargs)

        # Update total price from related OrderItems
        total = sum(
            item.price * item.quantity for item in self.orderitem_set.all()
        )
        if self.total_price != total:
            self.total_price = total
            super().save(update_fields=['total_price'])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} likes {self.product.name}"

class ReturnRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"ReturnRequest - {self.user.username} - {self.order_item.product.name}"


class NewsletterEmail(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email



class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating})"




class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    percentage = models.PositiveIntegerField(help_text="Discount percentage (e.g., 20 for 20%)")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.percentage}%"
