from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока."""

    video_url = serializers.URLField(validators=[validate_youtube_url])

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса."""

    is_subscribed = serializers.SerializerMethodField()

    lessons_count = serializers.SerializerMethodField()
    lesson_set = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        """Возвращает количество уроков курса."""
        return obj.lesson_set.count()

    def get_is_subscribed(self, obj):
        """Проверяет подписку пользователя на курс."""
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            return False

        return Subscription.objects.filter(
            user=request.user,
            course=obj
        ).exists()