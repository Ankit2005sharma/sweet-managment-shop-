from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'users'


class Sweet(models.Model):
    CATEGORY_CHOICES = [
        ('traditional', 'Traditional'),
        ('modern', 'Modern'),
        ('festival', 'Festival Special'),
        ('premium', 'Premium'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='traditional')
    image = models.CharField(max_length=10, default='🍬')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sweets')
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'sweets'
        ordering = ['-created_at']

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    sweet = models.ForeignKey(Sweet, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.sweet.name}"
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']