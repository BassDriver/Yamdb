import random

from django.db.models import Avg
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import viewsets, filters, status
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin)
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from api_yamdb.settings import ADMIN_EMAIL, CONFIRMATION_CODE_DEFAULT
from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import (IsAdminUserOrReadOnly,
                          ModeratorAdminOrReadOnly, IsOnlyAdmin)
from .serializers import (
    CategorySerializer,
    CommentSerializer, GenreSerializer, ReviewSerializer,
    SignUpSerializer, TitleCreateSerializer,
    TitleSerializer, TokenSerializer,
    UserSerializer, NotAdminSerializer
)


SUBJECT = 'Код подтверждения YaMDb'


class CategoryGenreViewSet(
        ListModelMixin,
        CreateModelMixin,
        DestroyModelMixin,
        GenericViewSet):
    queryset = None
    serializer_class = None
    filter_backends = [SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'
    permission_classes = (IsAdminUserOrReadOnly,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOnlyAdmin, ]
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)

    @action(
        detail=False, methods=['get', 'patch'],
        url_path='me', url_name='me',
        permission_classes=[IsAuthenticated, ]
    )
    def get_current_user_info(self, request):
        if not request.method == 'PATCH':
            return Response(UserSerializer(request.user).data)
        serializer = NotAdminSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class APISignUp(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        try:
            user, created = User.objects.get_or_create(
                username=username,
                email=email,
            )
        except IntegrityError:
            return Response(
                'Такой логин или email уже существуют',
                status=status.HTTP_400_BAD_REQUEST
            )
        user.confirmation_code = str(random.randint(000000, 999999))
        user.save()
        send_mail(
            'Код подверждения', user.confirmation_code,
            [ADMIN_EMAIL], (email, ), fail_silently=False
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class APIGetToken(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data.get('username')
        user = get_object_or_404(User, username=username)
        if (
            data.get('confirmation_code') == user.confirmation_code
            and data.get('confirmation_code') != CONFIRMATION_CODE_DEFAULT
        ):
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        user.confirmation_code = CONFIRMATION_CODE_DEFAULT
        user.save()
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'
             ' Необходимо получить новый код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(CategoryGenreViewSet):
    """API для работы с моделью категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    """API для работы с моделью жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """API для работы произведений"""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    ordering_fields = ('name',)
    serializer_class = TitleSerializer
    permission_classes = [IsAdminUserOrReadOnly, ]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """API для работы с моделью отзывов"""
    serializer_class = ReviewSerializer
    permission_classes = [ModeratorAdminOrReadOnly, ]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """API для работы с моделью комментариев"""
    serializer_class = CommentSerializer
    permission_classes = [ModeratorAdminOrReadOnly, ]

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
