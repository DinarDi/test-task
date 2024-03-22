from django.db.models import Count, Exists, OuterRef
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework import status

from api_v1.permissions import IsEnrolled
from api_v1.serializers.product_serializers import ProductSerializer, ProductWithLessonsSerializer
from product.models import Product, ProductAccess


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """"""
    queryset = Product.objects.all().annotate(
        lessons_count=Count('lessons')
    )
    serializer_class = ProductSerializer

    def get_queryset(self):
        if self.action == 'list':
            # Получить продукты доступные для покупки
            queryset = self.queryset.filter(
                ~Exists(
                    ProductAccess.objects.filter(product=OuterRef('pk'), user=self.request.user, is_valid=True)
                )
            )
            return queryset
        else:
            return self.queryset

    @action(
        methods=['post'],
        detail=True,
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated]
    )
    def enroll(self, request, *args, **kwargs):
        """Подписка на продукт"""
        product = self.get_object()
        access, created = ProductAccess.objects.get_or_create(
            product=product, user=request.user, is_valid=True
        )
        if created:
            return Response(status=status.HTTP_201_CREATED, data={'message': 'Enrolled'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Already exists'})

    @action(
        methods=['get'],
        detail=True,
        serializer_class=ProductWithLessonsSerializer,
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated, IsEnrolled]
    )
    def lessons(self, request, *args, **kwargs):
        """Получение уроков продукта"""
        return self.retrieve(request, *args, **kwargs)
