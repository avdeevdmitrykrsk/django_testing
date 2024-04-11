from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError
from pytest_lazyfixture import lazy_fixture

from news.forms import WARNING, BAD_WORDS
from news.models import Comment

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('clients', 'status', 'form_data'),
    (
        (lazy_fixture('client'), HTTPStatus.FOUND, {'text': 'asd'}),
    )
)
def test_non_auth_cant_create_comment(
    clients, status, form_data, detail_url_author
):
    """
    Проверка отпраки комментария.

        Проверка, что неаутентифицированный пользователь не может
        отправить комментарий.

            Порядок действий:
                1. Считаем количество коментариев.
                2. Делаем пост запрос.
                3. Снова считаем комментарии.
                4. Сравниваем.
    """
    comment_count_before_post_requset = Comment.objects.count()
    response = clients.post(
        detail_url_author, data=form_data
    )
    comment_count_after_post_requset = Comment.objects.count()
    assert (
        comment_count_before_post_requset == comment_count_after_post_requset
    )
    assert response.status_code == status


@pytest.mark.parametrize(
    ('clients'),
    (
        (lazy_fixture('author_client')),
    )
)
def test_auth_can_create_comment(
    clients, detail_url_author, news, comment_author
):
    """
    Проверка отпраки комментария.

        Проверка, что аутентифицированный пользователь может
        отправить комментарий.

            Порядок действий:
                1. Считаем количество коментариев.
                2. Делаем пост запрос.
                3. Снова считаем комментарии.
                4. Сравниваем количество.
                5. Сравниваем поля.
    """
    response = clients.get(detail_url_author)
    news = response.context['news']
    comment = news.comment_set.last()
    assert comment.news == comment_author.news
    assert comment.author == comment_author.author
    assert comment.text == comment_author.text


@pytest.mark.parametrize(
    ('comment', 'status'),
    (
        (lazy_fixture('comment_author'), HTTPStatus.FOUND),
    )
)
def test_possibility_to_delete_author_comment(
    author_client, news, comment, status, delete_url_author
):
    """Проверка доступа к странице удаления комментария."""
    comment_count_before_post_requset = Comment.objects.count()
    response = author_client.delete(delete_url_author)
    comment_count_after_post_requset = Comment.objects.count()
    assert comment_count_after_post_requset == (
        comment_count_before_post_requset - 1
    )
    assert response.status_code == status


@pytest.mark.parametrize(
    ('comment'),
    (
        (lazy_fixture('comment_author')),
    )
)
def test_possibility_to_edit_author_comment(
        author_client, news,
        comment,
        edit_url_author,
        edited_comment_author,
        detail_url_author
):
    """Проверка доступа к странице редактирования комментария."""
    author_client.post(edit_url_author, data=edited_comment_author)
    response = author_client.get(detail_url_author)
    news = response.context['news']
    comments = news.comment_set.last()
    assert comments.text == edited_comment_author['text']
    assert comments.author == edited_comment_author['author']
    assert comments.news == edited_comment_author['news']


@pytest.mark.parametrize(
    ('comment'),
    (
        (lazy_fixture('comment_not_author')),
    )
)
def test_possibility_to_edit_not_author_comment(
        author_client, news,
        comment,
        edit_url_not_author,
        edited_comment_author,
        detail_url_not_author
):
    """Проверка доступа к странице редактирования комментария."""
    author_client.post(edit_url_not_author, data=edited_comment_author)
    response = author_client.get(detail_url_not_author)
    news = response.context['news']
    comments = news.comment_set.last()
    assert comments.text == comment.text
    assert comments.author == comment.author
    assert comments.news == comment.news


@pytest.mark.parametrize(
    ('comment', 'status'),
    (
        (lazy_fixture('comment_not_author'), HTTPStatus.NOT_FOUND),
    )
)
def test_possibility_to_delete_not_author_comment(
    author_client, comment, status, delete_url_not_author
):
    """Проверка доступа к страницам удаления/редактирования комментария."""
    comment_count_before_post_requset = Comment.objects.count()
    response = author_client.delete(delete_url_not_author)
    comment_count_after_post_requset = Comment.objects.count()
    assert (
        comment_count_after_post_requset == comment_count_before_post_requset
    )
    assert response.status_code == status


def test_comment_for_bad_words(author_client, news):
    """Проверка на использование запретных слов."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data={'text': choice(BAD_WORDS)})
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
