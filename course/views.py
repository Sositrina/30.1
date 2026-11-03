from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курсов."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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
