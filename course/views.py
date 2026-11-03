from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModerator, IsOwner
from .paginators import CourseLessonPagination

from django.shortcuts import get_object_or_404


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курсов."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CourseLessonPagination

    def get_permissions(self):
        """Определяет права доступа для действий с курсами."""
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Назначает владельца при создании курса."""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Ограничивает список курсов для обычного пользователя."""
        if self.action == 'list':
            if not self.request.user.groups.filter(name='Модераторы').exists():
                return Course.objects.filter(owner=self.request.user)

        return Course.objects.all()


class LessonListAPIView(generics.ListAPIView):
    """Получение списка и создание уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CourseLessonPagination

    def get_queryset(self):
        """Возвращает уроки, доступные пользователю."""
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=self.request.user)

class LessonCreateAPIView(generics.CreateAPIView):
    """Получение списка и создание уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        """Назначает владельца при создании урока."""
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Получение и изменение урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]


class SubscriptionAPIView(APIView):
    """Добавление и удаление подписки на курс."""

    def post(self, request, *args, **kwargs):
        """Переключает подписку пользователя на курс."""
        user = request.user
        course_id = request.data.get('course')
        course_item = get_object_or_404(Course, pk=course_id)

        subs_item = Subscription.objects.filter(
            user=user,
            course=course_item
        )

        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'

        return Response({'message': message})
