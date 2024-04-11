from http import HTTPStatus

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


class TestNoteCreation(AddFixture):

    def test_anonymous_user_cant_create_comment(self):
        """Проверяем, что анонимный пользователь не может создать заметку."""
        notes_count_before_post_request = Note.objects.count()
        response = self.client.post(self.url_add, data=self.form_data)
        notes_count_after_post_request = Note.objects.count()
        self.assertEqual(
            notes_count_before_post_request, notes_count_after_post_request
        )
        redirect_url = f'{self.login_url}?next={self.url_add}'
        self.assertRedirects(response, redirect_url)

    def test_user_can_create_comment(self):
        """
        Проверка создания заметки.

            Проверяем, что аутентифицированный
            пользователь может создать заметку.

                Порядок действий:
                    1. Считаем количество заметок.
                    2. Делаем POST запрос.
                    3. Снова считаем количество заметок.
                    4. Сравнимаем количество ДО и ПОСЛЕ,
                        должно быть на 1 больше.
                    5. Проверяем, что новосозданная заметка является нашей,
                        путём проверки соответствия полей.

                Используемые методы:
                    1. assertEqual()
        """
        notes_count_before_post_request = Note.objects.count()
        self.auth_author.post(self.url_add, data=self.form_data)
        notes_count_after_post_request = Note.objects.count()
        self.assertEqual(
            notes_count_after_post_request, (
                notes_count_before_post_request + self.notes_difference_count
            )
        )
        note = Note.objects.last()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_impossible_to_create_two_notes_by_one_same_slug(self):
        """
        Проверка создания заметки.

            Проверяем, что невозможно создать две заметки
            с одинаковым полем 'slug'.

                Порядок действий:
                    1. Создаем заметку (slug - уникальный)
                    2. Считаем количество заметок.
                    3. Создаем вторую заметку с таким же slug.
                    4. Снова считаем количество заметок.
                    5. Проверяем, что при попытке POST запроса, форма
                        выдает ошибку в поле slug.
                    6. Дополнительно проверяем, что количество заметок
                        не увеличилось.

                Используемые методы:
                    1. assertFormError()
                    2. assertEqual()
        """
        self.auth_author.post(self.url_add, data=self.form_data)
        notes_count_before_post_request = Note.objects.count()
        response = self.auth_author.post(self.url_add, data=self.form_data)
        notes_count_after_post_request = Note.objects.count()
        self.assertEqual(
            notes_count_before_post_request, notes_count_after_post_request
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(
                f'{self.form_data["slug"]} - такой slug уже существует,'
                ' придумайте уникальное значение!'
            )
        )

    def test_create_note_with_no_slug(self):
        """
        Проверка создания заметки.

            Проверяем, что если при создании заметки не заполнен slug,
            то он формируется автоматически, с помощью функции
            pytils.translit.slugify.

                Порядок действий:
                    1. Считаем количество заметок.
                    2. Создаем заметку не заполнив поле slug.
                    3. Снова считаем количество заметок.
                    4. Сравниваем количество ДО и ПОСЛЕ post запроса,
                        должно быть на 1 больше.

                Используемые методы:
                    2. assertEqual()
        """
        notes_count_before_post_request = Note.objects.count()
        self.auth_author.post(self.url_add, data=self.form_data_no_slug)
        notes_count_after_post_request = Note.objects.count()
        self.assertEqual(
            notes_count_after_post_request, (
                notes_count_before_post_request + self.notes_difference_count
            )
        )
        note = Note.objects.last()
        self.assertEqual(note.slug, self.slug_for_note)

    def test_edit_pages(self):
        """
        Проверка страницы редактирования заметки.

            Проверяем, что пользователь может редактировать свои заметки,
            при этом не может редактировать чужие.

                Порядок действий:
                    1. Делаем post запрос к своей заметке с новыми данными.
                    2. Проверяем изменение данных.
                    3. Делаем post запрос к чужой заметке с новыми данными.
                    4. Проверяем что вернулась 404 ошибка.

                Используемые методы:
                    1. assertEqual()
        """
        self.auth_author.post(
            self.url_edit_note_author,
            data=self.edited_form_data_author
        )
        note = Note.objects.first()
        self.assertEqual(note.text, self.edited_form_data_author['text'])
        response = self.auth_author.post(
            self.url_edit_note_not_author,
            data=self.edited_form_data_not_author
        )
        note = Note.objects.last()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_pages(self):
        """
        Проверка страницы удаления заметки.

            Проверяем, что пользователь может удалять свои заметки,
            при этом не может удалять чужие.

            Порядок действий:
                    1. Считаем количество заметок.
                    2. Делаем delete запрос к своей заметке.
                    3. Снова считаем количество заметок,
                    4. Сравниваем количество заметок ДО и ПОСЛЕ delete запроса,
                        должно быть на 1 меньше.
                    5. Так же дополнительно проверяем что сработал редирект
                        после удаления.
                    6. Проверяем, что при попытке получить доступ к странице
                        удаления чужой записи, получаем ошибку 404.

                Используемые методы:
                    1. assertRedirect()
                    2. assertEqual()
        """
        notes_count_before_post_request = Note.objects.count()
        response_from_author_note = self.auth_author.delete(
            self.url_delete_note_author
        )
        notes_count_after_post_request = Note.objects.count()
        self.assertEqual(
            notes_count_after_post_request, notes_count_before_post_request - 1
        )
        self.assertRedirects(response_from_author_note, self.success_url)
        response_from_not_author_note = self.auth_author.delete(
            self.url_delete_note_not_author
        )
        self.assertEqual(
            response_from_not_author_note.status_code, HTTPStatus.NOT_FOUND
        )
