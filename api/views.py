from rest_framework import generics
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView
from api.models import User
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.

class HelloView(ListAPIView):

    queryset = User.objects.all()

