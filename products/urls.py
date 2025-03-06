from django.urls import path
from . import views



urlpatterns = [
    path('',views.ProductView.as_view(),name='products'),
    path('<str:slug>',views.ProductDetailView.as_view(),name='product-detail'),
    path('collection/',views.CollectionView.as_view(),name='collection'),
    path('collection/<str:slug>',views.CollectionDetailView.as_view(),name='collection-detail'),
    path('media/',views.ProductMediaView.as_view(),name='product-media'),
    path('media/<int:pk>',views.ProductMediaDetailView.as_view(),name='product-media-detail'),

    path('task-status/<str:task_id>',views.check_email_status,name='task-status'),

    path('test-websocket/',views.test_websocket_view,name='test-websocket'),
]
