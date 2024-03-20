# Generated by Django 5.0.3 on 2024-03-18 17:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=155, verbose_name='Название')),
                ('start_date', models.DateTimeField(verbose_name='Дата и время начала')),
                ('price', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Стоимость')),
                ('min_students_count', models.PositiveIntegerField(verbose_name='Минимальное количество учеников в группе')),
                ('max_students_count', models.PositiveIntegerField(verbose_name='Максимальное количество учеников в группе')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_valid', models.BooleanField(default=False, verbose_name='Валидация доступа')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product', verbose_name='Продукт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.AddConstraint(
            model_name='productaccess',
            constraint=models.UniqueConstraint(fields=('user', 'product'), name='product_user_access_unique'),
        ),
    ]