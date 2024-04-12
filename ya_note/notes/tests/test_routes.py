from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .fixtures import AddFixture

User = get_user_model()


class TestRoutes(AddFixture):

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
            with self.subTest(name=name):
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
        for path in urls:
            with self.subTest():
                url = reverse(path)
                response = self.auth_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_delete_detail_pages(self):
        """Проверяем, доступ страниц аутентифицированному пользователю."""
        urls = (
            ('notes:detail', (self.note_author.slug,)),
            ('notes:edit', (self.note_author.slug,)),
            ('notes:delete', (self.note_author.slug,))
        )
        user_statuses = (
            (self.auth_author, HTTPStatus.OK),
            (self.client, HTTPStatus.FOUND),
        )
        for item in user_statuses:
            user, status = item
            for path, args in urls:
                with self.subTest(
                    path=path, args=args, user=user, status=status
                ):
                    url = reverse(path, args=args)
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяем, что страницы редиректят
        неаутентифицированного пользователя.
        """
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note_author.slug,)),
            ('notes:edit', (self.note_author.slug,)),
            ('notes:delete', (self.note_author.slug,))
        )
        for item in urls:
            path, args = item
            url = reverse(path, args=args)
            redirect_url = f'{self.login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)
