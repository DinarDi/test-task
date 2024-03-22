from rest_framework import serializers

from api_v1.serializers.lesson_serializers import LessonSerializer
from product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Сериалайзер для продуктов"""
    lessons_count = serializers.IntegerField(read_only=True)
    start_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'start_date',
            'price', 'lessons_count',
        )


class ProductWithLessonsSerializer(serializers.ModelSerializer):
    """Сериалайзер для продуктов с уроками"""
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Product
        fields = ('title', 'lessons', )
