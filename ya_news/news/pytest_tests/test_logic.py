from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertFormError
from pytest_lazyfixture import lazy_fixture

from news.forms import WARNING


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('clients', 'status', 'form_data'),
    (
        (lazy_fixture('client'), HTTPStatus.FOUND, {'text': 'asd'}),
        (lazy_fixture('author_client'), HTTPStatus.OK, None),
    )
)
def test_non_auth_cant_create_comment(clients, status, news_id, form_data):
    """
    Проверка, что неаутентифицированный пользователь не может
    отправить комментарий, а аутентифицированный может.
    """
    url = reverse('news:detail', args=(news_id.id,))
    response = clients.post(url, data=form_data if form_data else None)
    assert response.status_code == status


@pytest.mark.django_db
def test_comment_for_bad_words(author_client, news_id):
    """Проверка на использование запретных слов."""
    url = reverse('news:detail', args=(news_id.id,))
    response = author_client.post(url, data={'text': 'негодяй'})
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'path',
    (
        ('news:edit'),
        ('news:delete')
    )
)
@pytest.mark.parametrize(
    ('comment', 'status'),
    (
        (lazy_fixture('comment_id'), HTTPStatus.OK),
        (lazy_fixture('comment_id2'), HTTPStatus.NOT_FOUND)
    )
)
def test_possibility_users_to_edit_delete_comment(
    author_client, news_id, path, comment, status
):
    """Проверка доступа к страницам удаления/редактирования комментария."""
    url = reverse(path, args=(news_id.id,))
    response = author_client.get(url)
    assert response.status_code == status
