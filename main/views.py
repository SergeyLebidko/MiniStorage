import os
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.http.response import FileResponse
from rest_framework.filters import SearchFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from io import BytesIO
from .serializers import ProductSerializer
from .authentication import TokenAuthentication
from .pagination import CustomPagination
from .models import Product, Token
from .utils import get_tmp_file_path, check_tmp_folder


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
    products_list = Product.objects.all()
    work_book = Workbook()
    work_sheet = work_book.active
    work_sheet.title = 'Products'

    # Создаем шапку таблицы
    for column, content in enumerate(['Номер', 'Наименование', 'Описание', 'Дата создания', 'Дата изменения'], 1):
        cell = work_sheet.cell(row=1, column=column, value=content)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    # Копируем данные из БД
    row = 2
    for product in products_list:
        work_sheet.cell(row=row, column=1, value=product.pk)
        work_sheet.cell(row=row, column=2, value=product.title)
        work_sheet.cell(row=row, column=3, value=product.description)
        work_sheet.cell(row=row, column=4, value=product.dt_created)
        work_sheet.cell(row=row, column=5, value=product.dt_updated)
        row += 1

    # Выставляем ширину столбцов
    work_sheet.column_dimensions[get_column_letter(2)].width = 80
    work_sheet.column_dimensions[get_column_letter(3)].width = 30
    work_sheet.column_dimensions[get_column_letter(4)].width = 25
    work_sheet.column_dimensions[get_column_letter(5)].width = 25

    # Сохраняем данные во временный файл, затем отдаем содержимое файла клиенту. Сам файл удаляем
    check_tmp_folder()
    tmp_file_path = get_tmp_file_path('products.xlsx')
    work_book.save(tmp_file_path)

    with open(tmp_file_path, 'rb') as file:
        bio = BytesIO(file.read())
    os.remove(tmp_file_path)

    return FileResponse(
        bio,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename='products.xlsx'
    )


# Методы API


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['id', 'title', 'description']

    def get_queryset(self):
        queryset = Product.objects.all()
        order = self.request.query_params.get('order')
        if order:
            queryset = queryset.order_by(order)
        return queryset
