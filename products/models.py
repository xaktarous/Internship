from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from users.models import User
from django.utils.text import slugify


class Product(models.Model):
    user=models.ForeignKey(User,blank=False,on_delete=models.CASCADE,related_name='user_media')
    name = models.CharField(max_length=255,blank=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2,blank=False,validators=[MinValueValidator(0)])
    stock_quantity=  models.PositiveIntegerField(blank=False,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug= models.SlugField(blank=True,null=True)
    
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['slug','user'],name='unique_product_name_username')
        ]

    def  save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock_quantity > 0
    
    def __str__(self):
        return self.name +" - "+ self.user.username + " - " + str(self.id)



class ProductMedia(models.Model):
    
    product = models.ForeignKey(Product,blank=False,on_delete=models.CASCADE,related_name='media')
    image = models.ImageField(upload_to='products/images/',blank=False,null=False)
    

    def __str__(self):
        return self.product.name +" - " + str(self.id)
    


class Collection(models.Model):
    name = models.CharField(max_length=255,blank=False)
    description = models.TextField()
    products = models.ManyToManyField(Product,blank=True,related_name='collections')
    user=models.ForeignKey(User,blank=False,on_delete=models.CASCADE)
    slug= models.SlugField(blank=True,null=True)
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['slug','user'],name='unique_collection_name_username')
        ]

   

    def  save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
   
    
    def __str__(self):
        return self.name +" - "+ self.user.username