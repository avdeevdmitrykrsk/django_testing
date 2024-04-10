import pytest

from django.urls import reverse
from pytest_lazyfixture import lazy_fixture

from yanews import settings


@pytest.mark.django_db
def test_news_count_and_order_on_home_page(client, news_for_home_page):
    """
    Проверка количества новостей на главной странице,
    а так же порядок их вывода на страницу.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.django_db
def test_comment_order(client, comments_for_home_page, news_id):
    """Проверяем сортировку комментариев на странице новости."""
    url = reverse('news:detail', args=(news_id.id,))
    response = client.get(url)
    news = response.context['news']
    all_coments = news.comment_set.all()
    all_time_fields = [comment.created for comment in all_coments]
    sorted_time_fields = sorted(all_time_fields)
    assert all_time_fields == sorted_time_fields


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('clients', 'status'),
    (
        (lazy_fixture('client'), False),
        (lazy_fixture('author_client'), True)
    )
)
def test_no_access_to_form_for_non_auth_user(clients, status, news_id):
    """
    Проверяем, что форма отправки комментария
    недоступна анонимному юзеру.
    """
    url = reverse('news:detail', args=(news_id.id,))
    response = clients.get(url)
    objects = response.context
    assert ('form' in objects) == status
