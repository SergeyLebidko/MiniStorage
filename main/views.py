from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import ProductSerializer
from .authentication import TokenAuthentication
from .pagination import CustomPagination
from .models import Product, Token


class Login(LoginView):
    template_name = 'main/login.html'

    def get_success_url(self):
        user = self.request.user
        token = self.request.POST['user_token']
        Token.objects.update_or_create(user=user, defaults={'token': token})
        return super(Login, self).get_success_url()


class Logout(LogoutView):
    next_page = reverse_lazy('index')


@login_required(login_url='login')
def index(request):
    return render(request, 'main/index.html', context={})

# Методы API


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
