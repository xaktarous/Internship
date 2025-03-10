# oauth/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

import urllib.parse


# add comment  here
# add comment 2 here

class SignupUser(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    def post(self, request):   
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserList(APIView):
    serializer_class =UserSerializer
    permission_classes = [IsAdminUser]  
    def get(self, request):
        users = User.objects.all()
        serializer = self.serializer_class(users,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserDetail(APIView):
    serializer_class =UserSerializer
    def get(self, request):
        user=User.objects.get(id=request.user.id)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        user=User.objects.get(id=request.user.id)
        serializer = self.serializer_class(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user=User.objects.get(id=request.user.id)
        user.delete()
        return Response("user is deleted",status=status.HTTP_204_NO_CONTENT)





