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
    description = models.TextField(verbose_name='Описание', null=True, blank=True, default='')
    price = models.IntegerField(verbose_name='Цена')

    def __str__(self):
        return '{number:<10}|{title}'.format(number=self.pk, title=self.title)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']


class Contractor(BaseDataModel):
    INDIVIDUAL = 'individual'
    ENTITY = 'entity'

    CONTRACTOR_CATEGORY = (
        (INDIVIDUAL, 'Физическое лицо'),
        (ENTITY, 'Юридическое лицо')
    )

    title = models.CharField(max_length=200, verbose_name='Наименование')
    category = models.CharField(max_length=20, choices=CONTRACTOR_CATEGORY, verbose_name='Категория')

    def __str__(self):
        return '{number:<10}|{title}'.format(number=self.pk, title=self.title)

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'
        ordering = ['title']


class Operation(models.Model):
    username = models.CharField(max_length=200, verbose_name='Пользователь', null=True, blank=True)
    operation = models.TextField(verbose_name='Операция')
    dt_created = models.DateTimeField(verbose_name='Дата и время операции', auto_now_add=True)

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'
        ordering = ['-dt_created']


class StorageItem(BaseDataModel):
    product = models.OneToOneField(Product, on_delete=models.PROTECT, verbose_name='Товар')
    count = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{str(self.product)} ({self.count})'

    class Meta:
        verbose_name = 'Товар на складе'
        verbose_name_plural = 'Товары на складе'


class Document(BaseDataModel):
    RECEIPT = 'receipt'
    EXPENSE = 'expense'

    DESTINATION_TYPES = (
        (RECEIPT, 'Приход'),
        (EXPENSE, 'Расход')
    )

    destination_type = models.CharField(max_length=7, choices=DESTINATION_TYPES, verbose_name='Тип документа')
    contractor = models.ForeignKey(Contractor, on_delete=models.PROTECT, verbose_name='Контрагент')
    apply_flag = models.BooleanField(verbose_name='Документ проведен', default=False)

    def __str__(self):
        return f'{self.pk} от: {str(self.dt_created)[:19]}'

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-dt_created']


class DocumentItem(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name='Документ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    count = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.product.title}. Количество {self.count}'

    class Meta:
        verbose_name = 'Товар в документе'
        verbose_name_plural = 'Товары в документе'
