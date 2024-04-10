from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'news'),
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', lazy_fixture('news_id')),
    )
)
def test_pages_availability_for_anonymous_user(client, path, news):
    """Проверка доступности страниц для анонимного пользователя."""
    url = reverse(path, args=((news.id,) if news else None))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    ('clients', 'status'),
    (
        (lazy_fixture('author_client'), HTTPStatus.OK),
        (lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('client'), None),
    )
)
@pytest.mark.parametrize(
    ('path', 'comment'),
    (
        ('news:edit', lazy_fixture('comment_id')),
        ('news:delete', lazy_fixture('comment_id'))
    )
)
def test_pages_availability_for_auth_user(clients, status, path, comment):
    """
    Проверка доступности/недоступности страниц редактирования и удаления
    комментария для пользователей.
    """
    url = reverse(path, args=(comment.id,))
    response = clients.get(url)
    if status:
        assert response.status_code == status
    else:
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        assertRedirects(response, expected_url)
