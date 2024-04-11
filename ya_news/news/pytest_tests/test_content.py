import pytest
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_and_order_on_home_page(
        client, news_for_home_page, home_url_reverse
):
    """
    Проверка главной страницы.

        Проверка количества новостей на главной странице,
        а так же порядок их вывода на страницу.

            Порядок действий:
                1. Получаем количество записей из словаря context.
                2. Сравниваем с нужным количеством.
                3. Получаем полный список записей.
                4. Создаем отсортированный список записей.
                5. Сравниваем 2 списка.
    """
    response = client.get(home_url_reverse)
    news_list = response.context['object_list']
    assert news_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


def test_comment_order(client, comments_for_home_page, news):
    """Проверяем сортировку комментариев на странице новости."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news = response.context['news']
    all_coments = news.comment_set.all()
    all_time_fields = [comment.created for comment in all_coments]
    sorted_time_fields = sorted(all_time_fields)
    assert all_time_fields == sorted_time_fields


@pytest.mark.parametrize(
    ('clients', 'status'),
    (
        (lazy_fixture('client'), False),
        (lazy_fixture('author_client'), True),
    )
)
def test_no_access_to_form_for_clients(
    clients, status, detail_url_author
):
    """Проверяем (не)доступность формы для клиентов."""
    response = clients.get(detail_url_author)
    objects = response.context
    assert ('form' in objects) == status


@pytest.mark.parametrize(
    ('clients', 'form'),
    (
        (lazy_fixture('author_client'), CommentForm),
    )
)
def test_form_to_clients(clients, form, detail_url_author):
    """Проверяем соответствие формы."""
    response = clients.get(detail_url_author)
    objects = response.context
    assert isinstance(objects['form'], form)
