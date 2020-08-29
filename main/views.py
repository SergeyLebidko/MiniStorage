from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .serializers import ProductSerializer
from .models import Product


class Login(LoginView):
    template_name = 'main/login.html'


class Logout(LogoutView):
    next_page = reverse_lazy('index')


@login_required(login_url='login')
def index(request):
    return render(request, 'main/index.html', context={})

# Методы API


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
