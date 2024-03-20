from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    """Модель продукта"""
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Автор',
    )
    title = models.CharField(
        max_length=155,
        verbose_name='Название',
    )
    start_date = models.DateTimeField(
        verbose_name='Дата и время начала',
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Стоимость',
    )
    min_students_count = models.PositiveIntegerField(
        verbose_name='Минимальное количество учеников в группе',
    )
    max_students_count = models.PositiveIntegerField(
        verbose_name='Максимальное количество учеников в группе',
    )

    def save(self, *args, **kwargs):
        # Валидация минимального и максимального количества учеников
        if self.min_students_count > self.max_students_count:
            raise ValueError('Минимальное количество не может быть больше максимального')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductAccess(models.Model):
    """Модель для хранения доступа пользователя к продукту после покупки"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
    )
    is_valid = models.BooleanField(
        default=False,
        verbose_name='Валидация доступа',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product', ],
                name='product_user_access_unique',
            )
        ]

    def __str__(self):
        return f'{self.user} {self.product}'
