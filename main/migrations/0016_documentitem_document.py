# Generated by Django 3.1 on 2020-10-02 10:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_document_apply_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentitem',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.document', verbose_name='Документ'),
            preserve_default=False,
        ),
    ]
