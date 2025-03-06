from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import re
# Create your models here.


        
class User(AbstractUser):
    email=models.EmailField(unique=True,blank=False,null=False)
    phone_number=models.CharField(max_length=15,blank=False,unique=True,null=False)
    updated_at=models.DateTimeField(auto_now=True)

    def clean(self):
        pattern=r"^\+\d{1,3}[-\s]?\d{9}$"
        if not re.match(pattern,self.phone_number):
            raise ValidationError("Invalid phone number format")
        if User.objects.filter(phone_number=self.phone_number).exclude(id=self.id).exists():
            raise ValidationError("Phone number already exists")

    def __str__(self):
        return self.username
    def save(self, *args, **kwargs):
        self.full_clean()
        # If the password is not already hashed, hash it
        if self.pk is None or not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)