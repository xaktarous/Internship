from products.models import Product,ProductMedia,Collection
from rest_framework import serializers
from django.utils.text import slugify
from django.db.utils import IntegrityError
from django.db import transaction


class ProductSerializer(serializers.ModelSerializer):
    
    media = serializers.SerializerMethodField()
    user=serializers.ReadOnlyField(source='user.username')
    class Meta:
        model=Product
        fields=("user","name","price","stock_quantity","in_stock","media")
        extra_kwargs = {
            "description": {
                "required": False,
            }
        }
    
    def validate_stock_quantity(self,value):
        if  self.instance is None and value ==0:
            raise serializers.ValidationError("cannot add product with zero stock quantity")
        return value
        
    def get_media(self,obj):
        return [media.image.url for media in obj.media.all()]
  
    def validate(self,data):
        user_id = self.context['user'].id 
        instance=self.instance
        if data.get('name') is None:
            slug=slugify(instance.name)
        else:
            slug=slugify(data['name'])
        
        if Product.objects.filter(slug=slug,user_id=user_id).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError({"name":"A product with this name already exists for this user."})
        data['slug']=slug
        return data
    

class ProductMediaSerializer(serializers.ModelSerializer):
   
    class Meta:
        model=ProductMedia
        fields=("id","product","image")

    def get_product(self,obj):
        return obj.product.name
    
    def validate(self,data):
        if self.instance and data.get('product') is None:
            if self.instance.product.user != self.context['user']:
                raise serializers.ValidationError("this product not exist")
        else:
            if data['product'].user != self.context['user']:
               raise serializers.ValidationError("this product not exist")
       
        return data

    



    
class CollectionSerializer(serializers.ModelSerializer):
    products=serializers.SerializerMethodField()
    

    user=serializers.ReadOnlyField(source='user.username')
    class Meta:
        model=Collection
        fields=("name","description","products","user")
    
    def get_products(self,obj):
        return [product.name for product in obj.products.all()]
    
    def validate(self,data):
        user_id = self.context['user'].id
        instance=self.instance
        if data.get('name') is None:
            slug=slugify(instance.name)
        else:
            slug=slugify(data['name'])
        if Collection.objects.filter(name=slug,user_id=user_id).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError({"name":"A collection with this name already exists for this user."})
        data['slug']=slug
        return data
    
    
    


    