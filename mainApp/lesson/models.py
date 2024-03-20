from django.db import models

from product.models import Product


class Lesson(models.Model):
    """Модель урока"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Уроки',
    )
    title = models.CharField(
        max_length=155,
        verbose_name='Название урока',
    )
    link = models.URLField(
        verbose_name='Ссылка на видео',
    )

    def __str__(self):
        return self.title
