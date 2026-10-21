from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView


router = DefaultRouter()
router.register('courses', CourseViewSet)

urlpatterns = [
    path('lessons/', LessonListCreateAPIView.as_view()),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view()),
] + router.urls