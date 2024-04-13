from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.tests.fixtures import AddFixture

User = get_user_model()


class TestRoutes(AddFixture):

    def test_main_pages_availability(self):
        """Проверяем, что главная страница и страницы регистрации
        доступны анонимному пользователю.
        """
        urls = (
            self.url_home,
            self.login_url,
            self.logout_url,
            self.signup_url
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Проверяем доступность страниц аутентифицированному пользователю."""
        urls = (
            self.list_page_url,
            self.url_add,
            self.success_url
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_delete_detail_pages(self):
        """Проверяем, доступ страниц аутентифицированному пользователю."""
        urls = (
            self.url_detail_note_author,
            self.url_edit_note_author,
            self.url_delete_note_author
        )
        user_statuses = (
            (self.auth_author, HTTPStatus.OK),
            (self.client, HTTPStatus.FOUND),
        )
        for item in user_statuses:
            user, status = item
            for url in urls:
                with self.subTest(
                    url=url, user=user, status=status
                ):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяем, что страницы редиректят
        неаутентифицированного пользователя.
        """
        urls = (
            self.list_page_url,
            self.url_add,
            self.success_url,
            self.url_detail_note_author,
            self.url_edit_note_author,
            self.url_delete_note_author
        )
        for url in urls:
            redirect_url = f'{self.login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)
