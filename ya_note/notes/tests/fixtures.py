from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class AddFixture(TestCase):
    NOTE_TITLE = 'Тестовый заголовок'
    NOTE_TEXT = 'Тестовый текст'
    NOTE_SLUG = 'test_slug'

    @classmethod
    def setUpTestData(cls):
        """Создаем фикстуры для тестов."""
        cls.author = User.objects.create(username='test_user')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.not_author = User.objects.create(username='test_user2')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'author': cls.author,
            'slug': cls.NOTE_SLUG
        }
        cls.form_data_no_slug = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'author': cls.author
        }
        cls.note_author = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug='test_slug_author',
            author=cls.author
        )
        cls.note_not_author = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug='test_slug_not_author',
            author=cls.not_author
        )
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.url_add = reverse('notes:add')
        cls.list_page_url = reverse('notes:list')
        cls.url_edit_note_author = reverse(
            'notes:edit', args=(cls.note_author.slug,)
        )
        cls.url_edit_note_not_author = reverse(
            'notes:edit', args=(cls.note_not_author.slug,)
        )
        cls.url_delete_note_author = reverse(
            'notes:delete', args=(cls.note_author.slug,)
        )
        cls.url_delete_note_not_author = reverse(
            'notes:delete', args=(cls.note_not_author.slug,)
        )
        cls.slug_for_note = slugify(cls.form_data_no_slug['title'])
        cls.notes_difference_count = 1
        cls.edited_form_data_author = {
            'title': cls.NOTE_TITLE,
            'text': 'Измененный текст.',
            'slug': cls.note_author.slug,
            'author': cls.author,
        }
        cls.edited_form_data_not_author = {
            'title': cls.NOTE_TITLE,
            'text': 'Измененный текст.',
            'slug': cls.note_not_author.slug,
            'author': cls.not_author,
        }
