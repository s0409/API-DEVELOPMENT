from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.crypto import get_random_string

# class CustomUserManager(BaseUserManager):
#     def create_user(self, mobile_number, password=None, **extra_fields):
#         if not mobile_number:
#             raise ValueError('The Mobile Number field must be set')
       
#         user = self.model(mobile_number=mobile_number, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, mobile_number, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
       
#         return self.create_user(mobile_number, password, **extra_fields)

class User(models.Model):
    ROLE_CHOICES = {
        ('advisor', 'Advisor'),
        ('user', 'User')
    }
    mobile_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    role = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    advisor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.mobile_number

    class Meta:
        db_table = 'users'


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'category'

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product'

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unique_link = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unique_link:
            # Generate a unique link for this purchase
            self.unique_link = get_random_string(length=20)
        super(Purchase, self).save(*args, **kwargs)

    def __str__(self):
        return f'Purchase by {self.user.name} - Product: {self.product.name}'
    
    class Meta:
        db_table = 'purchase'
    

