import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News
from yanews import settings


@pytest.fixture
def news_id():
    news = News.objects.create(
        title='Тестовый заголовок',
        text='Тестовый текст'
    )
    return news


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def comment_id(author, news_id):
    comment = Comment.objects.create(
        text='text',
        author=author,
        news=news_id
    )
    return comment


@pytest.fixture
def comment_id2(not_author, news_id):
    comment = Comment.objects.create(
        text='text',
        author=not_author,
        news=news_id
    )
    return comment


@pytest.fixture
def news_for_home_page():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text=f'Тестовый коммент {index}',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comments_for_home_page(news_id, author):
    comments_count = 10
    now = timezone.now()
    for index in range(comments_count):
        comment = Comment.objects.create(
            news=news_id,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
