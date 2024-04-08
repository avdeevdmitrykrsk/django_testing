from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создаем фикстуры для тестов."""
        cls.author = User.objects.create(username='тестовый Автор')
        cls.reader = User.objects.create(username='Тестовый Аноним')
        cls.note = Note.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            slug='test_slug',
            author=cls.author
        )

    def test_main_pages_availability(self):
        """Проверяем, что главная страница и страницы регистрации
        доступны анонимному пользователю.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        )
        for name in urls:
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Проверяем доступность страниц аутентифицированному пользователю."""
        urls = (
            'notes:list',
            'notes:add',
            'notes:success'
        )
        self.client.force_login(self.author)
        for path in urls:
            with self.subTest():
                url = reverse(path)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_delete_detail_pages(self):
        """Проверяем, что страницы доступны только
        аутентифицированному пользователю.
        """
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for item in user_statuses:
            user, status = item
            self.client.force_login(user)
            for path, args in urls:
                with self.subTest():
                    url = reverse(path, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяем, что страницы редиректят
        неаутентифицированного пользователя.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )
        for item in urls:
            path, args = item
            url = reverse(path, args=args)
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)
