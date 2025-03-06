from django.contrib import admin

from .models import User

from .forms import CustomAdminAuthenticationForm

admin.site.login_form = CustomAdminAuthenticationForm

admin.site.register(User)
