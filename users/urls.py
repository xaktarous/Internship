from django.urls import path
from . import views

# another comment
urlpatterns = [
    path("list/",views.UserList.as_view()),
    path("profile/",views.UserDetail.as_view()),
    path("signup/",views.SignupUser.as_view()),

]