from django.contrib import admin
from users.models import User
# Register your models here.
from django import forms
from .models import Product,ProductMedia,Collection



class ProductMediaInline(admin.TabularInline):
    model = ProductMedia


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductMediaInline
    ]

admin.site.register(Product, ProductAdmin)


class CollectionAdminForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "instance" in kwargs and kwargs["instance"]:
            user = kwargs["instance"].user  # Récupérer l'utilisateur sélectionné
            if user:
                self.fields['products'].queryset = Product.objects.filter(user=user)

class CollectionAdmin(admin.ModelAdmin):
    form = CollectionAdminForm
   

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "products":
            user_id = request.POST.get("user") or request.GET.get("user")  # Récupérer l'utilisateur sélectionné
            if user_id:
                kwargs["queryset"] = Product.objects.filter(user_id=user_id)
            else:
                kwargs["queryset"] = Product.objects.none()  # Pas de produits tant qu'on n'a pas d'utilisateur
        return super().formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(Collection, CollectionAdmin)