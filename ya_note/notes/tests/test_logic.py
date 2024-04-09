from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from pytils.translit import slugify
User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Тестовый заголовок'
    NOTE_TEXT = 'Тестовый текст'
    NOTE_SLUG = 'tesl_slug'

    @classmethod
    def setUpTestData(cls):
        """Создаем фикстуры для тестов."""
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='test_user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'author': cls.user,
            'slug': cls.NOTE_SLUG
        }
        cls.form_data_no_slug = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'author': cls.user
        }

    def test_anonymous_user_cant_create_comment(self):
        """Проверяем, что анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.url}'
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_comment(self):
        """
        Проверяем, что аутентифицированный
        пользователь может создать заметку.
        """
        self.auth_client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_impossible_to_create_two_notes_by_one_same_slug(self):
        """
        Проверяем, что невозможно создать две заметки
        с одинаковым полем 'slug'.
        """
        self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(
                f'{self.form_data["slug"]} - такой slug уже существует,'
                f' придумайте уникальное значение!'
            )
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_create_note_with_no_slug(self):
        """
        Проверяем, что если при создании заметки не заполнен slug,
        то он формируется автоматически, с помощью функции
        pytils.translit.slugify.
        """
        self.auth_client.post(self.url, data=self.form_data_no_slug)
        args = slugify(self.form_data_no_slug['title'])
        note = Note.objects.get()
        self.assertEqual(note.slug, args)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
