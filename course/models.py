from django.db import models


class Course(models.Model):
    """Модель курса."""

    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to='courses/')
    description = models.TextField()
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        """Возвращает название курса."""
        return self.title


class Lesson(models.Model):
    """Модель урока."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    preview = models.ImageField(upload_to='lessons/')
    video_url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    owner = models.ForeignKey( 'users.User', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        """Возвращает название урока."""
        return self.title


class Subscription(models.Model):
    """Подписка пользователя на курс."""

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        """Настройки модели подписки."""

        unique_together = ('user', 'course')
