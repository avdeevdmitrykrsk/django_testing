from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('reverse_url', 'parametrized_client', 'status'),
    (
        (
            lazy_fixture('edit_url_author'),
            lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('delete_url_author'),
            lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('detail_url_author'),
            lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('edit_url_not_author'),
            lazy_fixture('author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            lazy_fixture('delete_url_not_author'),
            lazy_fixture('author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            lazy_fixture('edit_url_author'),
            lazy_fixture('client'),
            HTTPStatus.FOUND
        ),
        (
            lazy_fixture('delete_url_author'),
            lazy_fixture('client'),
            HTTPStatus.FOUND
        ),
        (
            lazy_fixture('detail_url_author'),
            lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('home_url_reverse'),
            lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('login_url_reverse'),
            lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('logout_url_reverse'),
            lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('signup_url_reverse'),
            lazy_fixture('client'),
            HTTPStatus.OK
        )
    )
)
def test_pages_for_author_and_client(
    reverse_url, parametrized_client, status, comment_author
):
    """Проверка страниц на доступность."""
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.parametrize(
    ('reverse_url'),
    (
        (lazy_fixture('edit_url_author')),
        (lazy_fixture('delete_url_author'))
    )
)
def test_redirect_pages(
    reverse_url,
    login_url_reverse,
    comment_author,
    client
):
    """Проверка страниц на редиректы."""
    expected_url = f'{login_url_reverse}?next={reverse_url}'
    response = client.get(reverse_url)
    assertRedirects(response, expected_url)
