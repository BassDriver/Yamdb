import api_yamdb.settings as settings

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_year, validate_username


VALIDATION_ERROR = 'Вы не можете добавить более одного отзыва на произведение'


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер категорий"""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер жанров"""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер произведений"""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False,
        many=False
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        required=False,
        many=True
    )
    year = serializers.IntegerField(
        validators=[validate_year]
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериалайзер создания произведений"""
    genre = GenreSerializer(
        many=True
    )
    category = CategorySerializer()
    rating = serializers.IntegerField(
        required=False
    )

    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        )
        model = Title
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер комментариев"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        exclude = ('review',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер отзывов"""
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        exclude = ('title',)

    def validate_score(self, value):
        """Проверяем, что значение score от 1 до 10."""
        if value in range(1, 11):
            return value
        raise serializers.ValidationError(
            'Оценка должна быть в диапазоне от 1 до 10. '
            f'Было передано значение {value}'
        )

    def validate(self, data):
        """Проверяем уникальность отзыва."""
        if self.context['request'].method == 'POST' and Review.objects.filter(
            title=self.context['view'].kwargs.get('title_id'),
            author=self.context['request'].user
        ).exists():
            raise serializers.ValidationError('Второй отзыв оставить нельзя')
        return data


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )

        def validate_username(self, value):
            return validate_username(value)


class NotAdminSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer):

    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=[validate_username]
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
        validators=[validate_username]
    )
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_MAX_LENGTH,
        required=True
    )
