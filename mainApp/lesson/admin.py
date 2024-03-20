from django.contrib import admin

from lesson.models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['product', 'title', 'link']
