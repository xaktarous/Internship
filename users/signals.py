from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
 


@receiver([post_save],sender=User)
def sendmail_after_signup(sender,instance,created, **kwargs):
    if created:
            email=instance.email
            context={'username': instance.username}
            subject = render_to_string('emails/mail_subject.txt', context).strip()
            html_content = render_to_string('emails/mail_body.html', context)
            email_message = EmailMultiAlternatives(subject,html_content,settings.EMAIL_HOST_USER,[email])
            email_message.content_subtype = "html"
            email_message.send()