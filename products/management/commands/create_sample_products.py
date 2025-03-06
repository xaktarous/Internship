from django.core.management.base import BaseCommand
from products.models import Product
from users.models import User
from django.utils.text import slugify


class Command(BaseCommand):
    
    
    def handle(self, *args, **kwargs):
        user=User.objects.get(id=1)
        sample_products = [
            {"name": "Produit A", "price": 10.99, "stock_quantity": 50},
            {"name": "Produit B", "price": 20.49, "stock_quantity": 30},
            {"name": "Produit C", "price": 5.99, "stock_quantity": 100},
        ]

        # Création en masse des produits
        products = [
            Product(user=user, slug=slugify(data["name"]), **data) 
            for data in sample_products
        ]
       
        Product.objects.bulk_create(products)

        print(f'{len(products)} produits ajoutés avec succès !')
