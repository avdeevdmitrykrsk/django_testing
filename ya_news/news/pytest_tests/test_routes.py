from http import HTTPStatus as Sc

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('reverse_url', 'parametrized_client', 'status'),
    (
        (lf('edit_url_author'), lf('author_client'), Sc.OK),
        (lf('delete_url_author'), lf('author_client'), Sc.OK),
        (lf('detail_url_author'), lf('author_client'), Sc.OK),
        (lf('edit_url_not_author'), lf('author_client'), Sc.NOT_FOUND),
        (
            lf('delete_url_not_author'),
            lf('author_client'),
            Sc.NOT_FOUND,
        ),
        (lf('edit_url_author'), lf('client'), Sc.FOUND),
        (lf('delete_url_author'), lf('client'), Sc.FOUND),
        (lf('detail_url_author'), lf('client'), Sc.OK),
        (lf('home_url_reverse'), lf('client'), Sc.OK),
        (lf('login_url_reverse'), lf('client'), Sc.OK),
        (lf('logout_url_reverse'), lf('client'), Sc.OK),
        (lf('signup_url_reverse'), lf('client'), Sc.OK),
    ),
)
def test_pages_for_author_and_client(
    reverse_url, parametrized_client, status, comment_author
):
    """Проверка страниц на доступность."""
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.parametrize(
    ('reverse_url'), ((lf('edit_url_author')), (lf('delete_url_author')))
)
def test_redirect_pages(
    reverse_url, login_url_reverse, comment_author, client
):
    """Проверка страниц на редиректы."""
    expected_url = f'{login_url_reverse}?next={reverse_url}'
    response = client.get(reverse_url)
    assertRedirects(response, expected_url)
