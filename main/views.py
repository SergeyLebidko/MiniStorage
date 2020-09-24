import os
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.http.response import FileResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from io import BytesIO
from .models import Product, Contractor, Token
from utils import get_tmp_file_path, check_tmp_folder, model_to_xls


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


@login_required(login_url='login')
def products(request):
    return render(request, 'main/products.html', context={})


@login_required(login_url='login')
def contractors(request):
    return render(request, 'main/contractors.html', context={})


def products_to_xls(request):
    column_descriptions = [
        {'machine_name': 'id', 'display_name': 'Номер'},
        {'machine_name': 'title', 'display_name': 'Наименование', 'width': 80},
        {'machine_name': 'description', 'display_name': 'Описание', 'width': 30},
        {'machine_name': 'price', 'display_name': 'Цена'},
        {'machine_name': 'dt_created', 'display_name': 'Дата создания', 'width': 30},
        {'machine_name': 'dt_updated', 'display_name': 'Дата изменения', 'width': 30},
    ]
    xls_data = model_to_xls(Product, column_descriptions)

    return FileResponse(
        xls_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename='products.xlsx'
    )


def contractors_to_xls(request):
    column_descriptions = [
        {'machine_name': 'id', 'display_name': 'Номер'},
        {'machine_name': 'title', 'display_name': 'Наименование', 'width': 80},
        {'machine_name': 'category', 'display_name': 'Категория', 'width': 30,
         'subs': dict(Contractor.CONTRACTOR_CATEGORY)},
        {'machine_name': 'dt_created', 'display_name': 'Дата создания', 'width': 30},
        {'machine_name': 'dt_updated', 'display_name': 'Дата изменения', 'width': 30},
    ]
    xls_data = model_to_xls(Contractor, column_descriptions)

    return FileResponse(
        xls_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename='products.xlsx'
    )
