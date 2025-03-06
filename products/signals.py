from django.db.models.signals import post_delete
from products.models import ProductMedia
from django.dispatch import receiver
from django.core.files.storage import default_storage




@receiver(post_delete, sender=ProductMedia)
def delete_image_on_s3(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
    

