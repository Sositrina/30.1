from django.db import models


class Course(models.Model):
    """Модель курса."""

    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to='courses/')
    description = models.TextField()


class Lesson(models.Model):
    """Модель урока."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    preview = models.ImageField(upload_to='lessons/')
    video_url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
