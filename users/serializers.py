from .models import User
from rest_framework import serializers
import re
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_active = serializers.BooleanField(default=True)
    phone_number=serializers.CharField(max_length=15)
    class Meta:
        model = User
        fields = ('username','password', 'email', 'is_staff', 'phone_number','is_active')

    def validate_phone_number(self, value):
        try:
            pattern = r"^\+\d{1,3}[-\s]\d{9}$"
            if not re.match(pattern, value):
               raise serializers.ValidationError("Invalid phone number format")
            else:
                if User.objects.filter(phone_number=value).exclude(id=self.instance.id if self.instance else None).exists():
                    raise serializers.ValidationError("Phone number already exists")
                else:
                    return value
        except ValueError:
            raise serializers.ValidationError("Phone number must be a valid integer")
        
    
        
    
    
    
        
        
    
  
    
