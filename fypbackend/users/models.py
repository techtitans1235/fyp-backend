from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(
        max_length=10, 
        choices=[
            ('customer', 'Customer'),
            ('admin', 'Admin'),
        ], 
        default='customer'
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"