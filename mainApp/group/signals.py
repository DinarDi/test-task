from logging import getLogger

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Count

from group.models import Group
from group.utils import Refresher
from product.models import ProductAccess


logger = getLogger(__name__)


@receiver(post_save, sender=ProductAccess)
def create_group(sender, instance, created, *args, **kwargs):
    """
    Создание группы или добавление в существующую,
    после получения пользователем доступа к продукту
    """
    user = instance.user
    product = instance.product

    groups = Group.objects.filter(product=product).annotate(
        students_count=Count('students')
    ).select_related('product').prefetch_related('students')

    refresher = Refresher(product=product, groups=list(groups))
    if created:
        if instance.is_valid:
            refresher.user = user
            group_for_user = refresher.add_student_to_group()
            logger.info(f'Пользователь {user.username} добавлен в группу {group_for_user.name}')
        else:
            # Нет доступа к продукту
            logger.info('Invalid access valid')
            return
    else:
        if instance.is_valid:
            # Доступ возвращен
            refresher.user = user
            group_for_user = refresher.add_student_to_group()
            logger.info(f'Доступ к продукту {product.title} возвращен. Пользователь {user.username} добавлен в группу {group_for_user.name}')
        else:
            # Нет доступа
            logger.info(f'Пользователю {user.username} запрещен доступ к продукту {product.title}')
            group = Group.objects.filter(product=product, students=user).first()
            group.students.remove(user)
            refresher.refresh_groups()
