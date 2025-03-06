import graphene
from graphene_django.types import DjangoObjectType
from users.models import User
from .models import Product  # Import your model

# Define a GraphQL type for the Product model

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")

class ProductType(DjangoObjectType):
    user=graphene.Field(UserType)
    class Meta:
        model = Product
        fields = "__all__"

# Define Query
class Query(graphene.ObjectType):
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, slug=graphene.String(required=True),username=graphene.String(required=True))
    def resolve_all_products(self, info, **kwargs):
        return Product.objects.select_related('user').all()

    def resolve_product(self, info, slug,username):
        return Product.objects.select_related('user').get(slug=slug, user__username=username)

# Create the schema
schema = graphene.Schema(query=Query)
