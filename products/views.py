from products.models import Product,ProductMedia,Collection
from .serializers import ProductSerializer,CollectionSerializer,ProductMediaSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Prefetch
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django_elasticsearch_dsl.search import Search
from .documents import ProductDocument
from .filters import ProductFilter
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from .tasks import check_stock
from celery.result import AsyncResult
from django.http import JsonResponse
from django.utils.text import slugify
from django.shortcuts import render

def test_websocket_view(request):
    return render(request, "test_websocket.html")


def check_email_status(request,task_id):
    result = AsyncResult(task_id)
    return JsonResponse({
        "task_id": task_id,
        "status": result.status,  
        "result": result.result  
    })


class ProductView(APIView):

    serializer_class = ProductSerializer
    
    def get(self,request):
        products = Product.objects.prefetch_related("media").filter(user=request.user)
        search_query = request.GET.get("search","")
        print(search_query)
        if search_query:
            search = ProductDocument.search().filter(
                'term', user_id=request.user.id
            ).query(
                'match',
                name=search_query 
            )
            try:
                response = search.execute()
                product_ids = [pro.meta.id for pro in response]
                products = products.filter(id__in=product_ids)
            except Exception as e:
                return Response({"error": str(e)})
            
        filtered_products = ProductFilter(request.GET,queryset=products).qs
        paginator = PageNumberPagination()
        paginator.page_size = 10  
        paginated_products = paginator.paginate_queryset(filtered_products, request)
        serializer = self.serializer_class(paginated_products,many=True)
        return paginator.get_paginated_response(serializer.data)
        
    
    def post(self,request):
        data=request.data
        if isinstance(data,list):
            serializer = self.serializer_class(data=data, context={'user': request.user}, many=True)
            if serializer.is_valid():
                products = [
                Product(user=request.user, **validated)
                for validated in serializer.validated_data
               ]
                created_products=Product.objects.bulk_create(products)
                for prod_data,created_product in zip(data,created_products):
                    for image in prod_data.get("image",[]):
                        ProductMedia.objects.create(product=created_product,image=image)
                return Response(self.serializer_class(created_products, many=True).data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        else:
            serializer = self.serializer_class(data=request.data, context={'user': request.user})
            if serializer.is_valid():
                product = serializer.save(user=request.user)
                for image in request.FILES.getlist("image"):
                    ProductMedia.objects.create(product=product,image=image)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        



class ProductDetailView(APIView):
    serializer_class = ProductSerializer
    def get(self,request,slug):
        if  Product.objects.filter(slug=slug,user=request.user).exists():
            product=Product.objects.prefetch_related("media").filter(user=request.user).get(slug=slug)
            serializer = self.serializer_class(product)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response("this product not exist",status.HTTP_404_NOT_FOUND)
    
    def put(self,request,slug):
        if not Product.objects.filter(slug=slug,user=request.user).exists():
            return Response("this product not exist",status.HTTP_404_NOT_FOUND) 
        product=Product.objects.prefetch_related("media").filter(user=request.user).get(slug=slug)
        serializer = self.serializer_class(product,data=request.data,partial=True,context={'user':request.user})
        if serializer.is_valid():
            product=serializer.save(user=request.user)
            if product.stock_quantity==0:
               task_ids=check_stock.delay()
               return Response({"task_id":str(task_ids),"data":serializer.data},status=status.HTTP_200_OK)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,slug):
        if not Product.objects.filter(slug=slug,user=request.user).exists():
            return Response("this product not exist",status.HTTP_404_NOT_FOUND)
        product=Product.objects.prefetch_related("media").filter(user=request.user).get(slug=slug)
        product.delete()
        return Response({"product":"product deleted"},status=status.HTTP_204_NO_CONTENT)
    



class ProductMediaView(APIView):
    serializer_class = ProductMediaSerializer
    def get(self,request):
        product_media = ProductMedia.objects.prefetch_related("product").filter(product__user=request.user)
        serializer = self.serializer_class(product_media,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request):
        serializer = self.serializer_class(data=request.data,context={'user':request.user})
        if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class ProductMediaDetailView(APIView):
    serializer_class = ProductMediaSerializer
    def get(self,request,pk):
        if not ProductMedia.objects.filter(id=pk,product__user=request.user).exists():
            return Response("this product media not exist",status.HTTP_404_NOT_FOUND)
        product_media=ProductMedia.objects.prefetch_related("product").filter(product__user=request.user).get(id=pk)
        serializer = self.serializer_class(product_media)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self,request,pk):
        if not ProductMedia.objects.filter(id=pk,product__user=request.user).exists():
            return Response("this product media not exist",status.HTTP_404_NOT_FOUND)
        product_media=ProductMedia.objects.prefetch_related("product").filter(product__user=request.user).get(id=pk)
        serializer = self.serializer_class(product_media,data=request.data,partial=True,context={'user':request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        if not ProductMedia.objects.filter(id=pk,product__user=request.user).exists():
            return Response("this product media not exist",status.HTTP_404_NOT_FOUND)
        product_media=ProductMedia.objects.prefetch_related("product").filter(product__user=request.user).get(id=pk)
        product_media.delete()
        return Response({"product media":"product media deleted"},status=status.HTTP_204_NO_CONTENT)
    




class CollectionView(APIView):
    serializer_class = CollectionSerializer
    def get(self,request):
        collections = Collection.objects.prefetch_related("products").filter(user=request.user)
        serializer = self.serializer_class(collections,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):

        serializer = self.serializer_class(data=request.data,context={'user':request.user})
        if serializer.is_valid():
            products_names = request.data.get("products",[])
            product_col= Product.objects.filter(name__in=products_names,user=request.user)
            if len(product_col)==len(products_names):
                collection=serializer.save(user=request.user)
                collection.products.add(*product_col)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response({"products":"products not found"},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


class CollectionDetailView(APIView):
    serializer_class = CollectionSerializer
    def get(self,request,slug):
        if  Collection.objects.filter(slug=slug,user=request.user).exists():
            collection=Collection.objects.prefetch_related("products").filter(user=request.user).get(slug=slug)
            serializer = self.serializer_class(collection)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response("this collection not exist",status.HTTP_404_NOT_FOUND)

    def put(self,request,slug):
        if not Collection.objects.filter(slug=slug,user=request.user).exists():
            return Response("this collection not exist",status.HTTP_404_NOT_FOUND)
        collection=Collection.objects.prefetch_related("products").filter(user=request.user).get(slug=slug)
        serializer = self.serializer_class(collection,data=request.data,partial=True,context={'user':request.user})
        if serializer.is_valid():
            products_names = request.data.get("products",[])
            product_col= Product.objects.filter(name__in=products_names,user=request.user)
            if len(product_col)==len(products_names):
                collection=serializer.save(user=request.user)
                collection.products.add(*product_col)
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response({"products":"products not found"},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,slug):
        if not Collection.objects.filter(slug=slug,user=request.user).exists():
            return Response("this collection not exist",status.HTTP_404_NOT_FOUND)
        collection=Collection.objects.prefetch_related("products").filter(user=request.user).get(slug=slug)
        collection.delete()
        return Response({"collection":"collection deleted"},status=status.HTTP_204_NO_CONTENT)
    
     

    







