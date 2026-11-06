from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (CourseViewSet,
                    LessonListAPIView,
                    LessonCreateAPIView,
                    LessonRetrieveUpdateAPIView,
                    LessonDestroyAPIView,
                    SubscriptionAPIView)

router = DefaultRouter()
router.register('courses', CourseViewSet)

urlpatterns = [
                  path('lessons/', LessonListAPIView.as_view()),
                  path('lessons/create/', LessonCreateAPIView.as_view()),
                  path('lessons/<int:pk>/', LessonRetrieveUpdateAPIView.as_view()),
                  path('lessons/<int:pk>/delete/', LessonDestroyAPIView.as_view()),
                  path('subscriptions/', SubscriptionAPIView.as_view()),
              ] + router.urls
