from django.db import models
from django.contrib.auth.models import User

from product.models import Product


class Group(models.Model):
    """Модель группы"""
    name = models.CharField(
        max_length=155,
        verbose_name='Название группы',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name='Продукт',
    )
    students = models.ManyToManyField(
        User,
        blank=True,
        verbose_name='Ученики',
    )

    class Meta:
        ordering = ('-id', )

    def __str__(self):
        return self.name
