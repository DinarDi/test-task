from rest_framework.permissions import BasePermission

from product.models import ProductAccess


class IsEnrolled(BasePermission):
    message = 'Enroll to product for check lessons'

    def has_object_permission(self, request, view, obj):
        return ProductAccess.objects.filter(product=obj, user=request.user, is_valid=True).exists()
