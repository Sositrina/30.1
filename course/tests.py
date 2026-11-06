from rest_framework.test import APITestCase

from users.models import User
from course.models import Course, Lesson, Subscription

from django.contrib.auth.models import Group


class LessonTestCase(APITestCase):
    """Тестирование уроков."""

    def setUp(self):
        """Создаёт данные для тестов."""
        self.user = User.objects.create(
            email='test32@mail.com'
        )

        self.course = Course.objects.create(
            title='Тестовый курс',
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            title='Тестовый урок',
            description='Описание урока',
            video_url='https://www.youtube.com/watch?v=123',
            course=self.course,
            owner=self.user
        )

        self.client.force_authenticate(user=self.user)

    def test_get_lessons_list(self):
        """Проверяет получение списка уроков."""
        response = self.client.get('/lessons/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['title'],
            self.lesson.title
        )


    def test_get_lesson_detail(self):
        """Проверяет получение одного урока."""
        response = self.client.get(
            f'/lessons/{self.lesson.pk}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['title'],
            self.lesson.title
        )


    def test_create_lesson(self):
        """Проверяет создание урока."""
        with open('course/test.png', 'rb') as preview:
            data = {
                'title': 'Новый урок',
                'description': 'Описание нового урока',
                'video_url': 'https://www.youtube.com/watch?v=456',
                'course': self.course.pk,
                'preview': preview
            }

            response = self.client.post('/lessons/create/', data, format='multipart')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lesson.objects.count(), 2)


    def test_update_lesson(self):
        """Проверяет обновление урока."""
        data = {
            'title': 'Обновлённый урок'
        }

        response = self.client.patch(
            f'/lessons/{self.lesson.pk}/',
            data
        )

        self.assertEqual(response.status_code, 200)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновлённый урок')


    def test_delete_lesson(self):
        """Проверяет удаление урока."""
        response = self.client.delete(
            f'/lessons/{self.lesson.pk}/delete/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Lesson.objects.count(), 0)


    def test_create_lesson_invalid_url(self):
        """Проверяет запрет сторонних ссылок."""
        with open('course/test.png', 'rb') as preview:
            data = {
                'title': 'Урок с ошибкой',
                'description': 'Проверка валидатора',
                'video_url': 'https://example.com/video',
                'course': self.course.pk,
                'preview': preview
            }

            response = self.client.post(
                '/lessons/create/',
                data,
                format='multipart'
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Lesson.objects.count(), 1)
        self.assertIn('video_url', response.data)


    def test_get_lessons_unauthorized(self):
        """Проверяет доступ без авторизации."""
        self.client.force_authenticate(user=None)

        response = self.client.get('/lessons/')

        self.assertEqual(response.status_code, 401)


    def test_get_other_user_lesson(self):
        """Проверяет запрет доступа к чужому уроку."""
        other_user = User.objects.create(
            email='other32@mail.com'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.get(
            f'/lessons/{self.lesson.pk}/'
        )

        self.assertEqual(response.status_code, 403)


    def test_update_other_user_lesson(self):
        """Проверяет запрет изменения чужого урока."""
        other_user = User.objects.create(
            email='other32@mail.com'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.patch(
            f'/lessons/{self.lesson.pk}/',
            {'title': 'Чужое изменение'}
        )

        self.assertEqual(response.status_code, 403)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Тестовый урок')


    def test_delete_other_user_lesson(self):
        """Проверяет запрет удаления чужого урока."""
        other_user = User.objects.create(
            email='other32@mail.com'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.delete(
            f'/lessons/{self.lesson.pk}/delete/'
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Lesson.objects.count(), 1)


    def test_moderator_update_lesson(self):
        """Проверяет изменение урока модератором."""
        moderator = User.objects.create(
            email='moderator32@mail.com'
        )

        group = Group.objects.create(name='Модераторы')
        moderator.groups.add(group)

        self.client.force_authenticate(user=moderator)

        response = self.client.patch(
            f'/lessons/{self.lesson.pk}/',
            {'title': 'Изменено модератором'}
        )

        self.assertEqual(response.status_code, 200)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Изменено модератором')


    def test_add_subscription(self):
        """Проверяет добавление подписки."""
        response = self.client.post(
            '/subscriptions/',
            {'course': self.course.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['message'],
            'Подписка добавлена'
        )
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )


    def test_delete_subscription(self):
        """Проверяет удаление подписки."""
        Subscription.objects.create(
            user=self.user,
            course=self.course
        )

        response = self.client.post(
            '/subscriptions/',
            {'course': self.course.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['message'],
            'Подписка удалена'
        )
        self.assertEqual(Subscription.objects.count(), 0)