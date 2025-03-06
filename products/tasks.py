from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Product
import logging
from celery.result import AsyncResult



@shared_task(bind=True)  
def send_alert_email(self,product_id):
    try:
        product = Product.objects.get(id=product_id)
        subject = 'Stock Alert'
        message = f'The product "{product.name}" is running low on stock. Please restock it.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [product.user.email]
        send_mail(subject, message, from_email, recipient_list)
        return f"✅ Alert email sent for product ID {product_id}"
    except Product.DoesNotExist:
        self.update_state(state="FAILURE", meta={'error': f'Product {product_id} not found'})
        return f"❌ Product with ID {product_id} does not exist"

    except Exception as e:
        self.update_state(state="FAILURE", meta={'error': str(e)})
        return f"❌ Error sending alert email for product ID {product_id}: {str(e)}"




@shared_task
def check_stock():
    tasks = []
    products = Product.objects.filter(stock_quantity=0)
    for product in products:
       task=send_alert_email.delay(product.id) 
       tasks.append(task.id)

    return {"tasks": tasks} if tasks else {"message": "No products found"}
     
   