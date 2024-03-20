import copy
import datetime
import random
import string
from logging import getLogger

from django.contrib.auth.models import User
from django.db.models import Count

from group.models import Group
from product.models import Product

logger = getLogger(__name__)


class Refresher:
    user: User | None = None
    product: Product
    groups: list[Group]

    def __init__(
            self,
            product: Product,
            groups: list[Group],
            user: User | None = None,
    ):
        self.user = user
        self.product = product
        self.groups = groups

    def _is_product_started(self):
        """Проверка начались ли занятия по продукту"""
        now = datetime.datetime.now(datetime.UTC)
        if self.product.start_date < now:
            return True
        return False

    def _is_need_to_refresh(self, current_count: int):
        """Проверка надо ли перемешивать группы"""
        if current_count % self.product.max_students_count == 0:
            return True
        max_count = max(self.groups, key=lambda group: group.students_count)
        min_count = min(self.groups, key=lambda group: group.students_count)
        return max_count.students_count - min_count.students_count > 1

    def _create_name_for_group(self):
        """Создать имя для новой группы"""
        random.seed()
        name = ''.join(random.choices(string.ascii_lowercase, k=10))
        nums = random.randint(1, 100)
        return f'{self.product.title}_{name}_{nums}'

    def _create_group(self):
        """Создать новую группу"""
        group = Group.objects.create(
            name=self._create_name_for_group(),
            product=self.product,
        )
        group.save()
        return group

    def _create_group_with_user(self):
        """Создать новую группу и добавить пользователя"""
        group = Group.objects.create(
            name=self._create_name_for_group(),
            product=self.product
        )
        group.students.add(self.user)
        group.save()
        return group

    def _get_groups_count_for_current_students(
            self,
            current_students_count: int,
            current_g_count: int,
    ) -> dict[str, int]:
        """Вернуть требуемое количество групп для текущего количества студентов"""
        groups_count = current_g_count
        avg_students_count_in_groups = current_students_count // groups_count
        if avg_students_count_in_groups < self.product.min_students_count:
            groups_count += 1
            return self._get_groups_count_for_current_students(current_students_count, groups_count)
        if avg_students_count_in_groups > self.product.max_students_count:
            groups_count -= 1
            return self._get_groups_count_for_current_students(current_students_count, groups_count)
        if current_students_count % avg_students_count_in_groups:
            groups_count += 1
        return {
                'students_count_in_group': avg_students_count_in_groups,
                'groups_count': groups_count,
            }

    def add_student_to_group(self):
        """Добавление студента в группу"""
        user_group: Group | None = None

        if len(self.groups) == 0:
            # Создать группу с пользователем
            return self._create_group_with_user()

        # Группа с наименьшим количеством учеников
        min_students_count_group = min(self.groups, key=lambda group: group.students_count)

        if min_students_count_group.students_count == self.product.max_students_count:
            # Если количество равняется максимально допустимому, значит группа полная
            user_group = self._create_group_with_user()
            logger.info('Пользователь добавляется в новую группу, так как прошлые заполнены')
        else:
            # Иначе добавить в группу с минимальным количеством
            logger.info('Пользователь добавляется в группу с наименьшим количеством участников')
            min_students_count_group.students.add(self.user)
            user_group = min_students_count_group

        if self._is_product_started():
            return user_group

        # Refresh
        self.refresh_groups()

        return Group.objects.filter(
            product=self.product,
            students=self.user,
        ).first()

    def refresh_groups(self):
        """Обновление групп"""
        if self._is_product_started():
            logger.info('Продукт начался, нельзя обновлять группы')
            return

        current_groups: list[Group] = list(Group.objects.filter(product=self.product).annotate(
            students_count=Count('students')
        ))
        self.groups = current_groups
        current_groups_count = len(self.groups)  # Текущее количество групп
        current_students_count = sum(group.students_count for group in self.groups)  # Текущее количество учеников
        groups_count_with_students: dict[str, int] | None = None

        if not self._is_need_to_refresh(current_count=current_students_count):
            logger.info('Группы не нуждаются в обновлении')
            return

        all_students: list[User] = []  # Список всех учеников
        for group in self.groups:
            all_students.extend(group.students.all())

        if current_students_count % self.product.max_students_count == 0:
            logger.info('Количество учеников кратно максимально заданному для групп')
            groups_count_with_students = {
                'students_count_in_group': self.product.max_students_count,
                'groups_count': current_students_count / self.product.max_students_count,
            }
        else:
            # Найти количество групп при котором их заполнение будет отличаться на 1
            logger.info('Поиск нужного количества групп')
            groups_count_with_students = self._get_groups_count_for_current_students(
                current_students_count,
                copy.copy(current_groups_count),
            )

        # Поделить учеников на группы
        students_for_groups: list[list[User]] = [
            all_students[i:i + groups_count_with_students['students_count_in_group']]
            for i in range(0, len(all_students), groups_count_with_students['students_count_in_group'])
        ]

        # Добавить учеников в группы
        for index, users_in_group in enumerate(students_for_groups):
            is_clear = True
            if current_groups_count <= index:
                group = self._create_group()
                is_clear = False
            else:
                group = self.groups[index]

            group.students.set(users_in_group, clear=is_clear)

        # Удалить лишние группы
        if groups_count_with_students['groups_count'] < current_groups_count:
            for_delete = [
                group.pk for group
                in self.groups[int(abs(groups_count_with_students['groups_count'] - current_groups_count)):]
            ]
            Group.objects.filter(id__in=for_delete).delete()
