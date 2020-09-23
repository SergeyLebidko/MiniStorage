from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    token = models.CharField(max_length=32, verbose_name='Токен')
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    def __str__(self):
        return f'Токен {self.token} для пользователя {self.user}'

    class Meta:
        verbose_name = 'Токен пользователя'
        verbose_name_plural = 'Токены пользователей'


class BaseDataModel(models.Model):
    dt_created = models.DateTimeField(verbose_name='Дата и время создания', auto_now_add=True)
    dt_updated = models.DateTimeField(verbose_name='Дата и время последнего изменения', auto_now=True)
    to_remove = models.BooleanField(verbose_name='Помечен на удаление', null=False, default=False)

    class Meta:
        abstract = True


class Product(BaseDataModel):
    title = models.CharField(max_length=200, verbose_name='Наименование')
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    price = models.IntegerField(verbose_name='Цена')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']


class Contractor(BaseDataModel):
    CONTRACTOR_CATEGORY = (
        ('individual', 'Физическое лицо'),
        ('entity', 'Юридическое лицо')
    )

    title = models.CharField(max_length=200, verbose_name='Наименование')
    category = models.CharField(max_length=20, choices=CONTRACTOR_CATEGORY, verbose_name='Категория')

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'
        ordering = ['title']
