# Generated by Django 3.1 on 2020-09-29 17:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20200928_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storageitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.product', verbose_name='Товар'),
        ),
    ]
