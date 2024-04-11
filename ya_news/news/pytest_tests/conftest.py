from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News
from django.conf import settings


@pytest.fixture
def news():
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
def comment_author(author, news):
    comment = Comment.objects.create(
        text='тестовый текст',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def comment_not_author(not_author, news):
    comment = Comment.objects.create(
        text='тестовый',
        author=not_author,
        news=news
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
def comments_for_home_page(news, author):
    comments_count = 10
    now = timezone.now()
    for index in range(comments_count):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def edit_url_author(comment_author):
    return reverse('news:edit', args=(comment_author.id,))


@pytest.fixture
def delete_url_author(comment_author):
    return reverse('news:delete', args=(comment_author.id,))


@pytest.fixture
def detail_url_author(comment_author):
    return reverse('news:detail', args=(comment_author.id,))


@pytest.fixture
def detail_url_not_author(comment_not_author):
    return reverse('news:detail', args=(comment_not_author.id,))


@pytest.fixture
def edit_url_not_author(comment_not_author):
    return reverse('news:edit', args=(comment_not_author.id,))


@pytest.fixture
def delete_url_not_author(comment_not_author):
    return reverse('news:delete', args=(comment_not_author.id,))


@pytest.fixture
def home_url_reverse():
    return reverse('news:home')


@pytest.fixture
def login_url_reverse():
    return reverse('users:login')


@pytest.fixture
def logout_url_reverse():
    return reverse('users:logout')


@pytest.fixture
def signup_url_reverse():
    return reverse('users:signup')


@pytest.fixture
def edited_comment_author(author, news):
    return {
        'text': 'измененный текст',
        'author': author,
        'news': news
    }
