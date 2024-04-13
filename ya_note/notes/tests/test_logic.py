from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.models import Note
from notes.tests.fixtures import AddFixture

User = get_user_model()


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

    def test_edit_note_author(self):
        """
        Проверка страницы редактирования заметки.

            Проверяем, что пользователь может редактировать свои заметки.

                Порядок действий:
                    1. Делаем post запрос к своей заметке с новыми данными.
                    2. Проверяем поля.

                Используемые методы:
                    1. assertEqual()
        """
        self.auth_author.post(
            self.url_edit_note_author,
            data=self.edited_form_data_author
        )
        note = Note.objects.get(pk=self.note_author.id)
        self.assertEqual(note.title, self.edited_form_data_author['title'])
        self.assertEqual(note.text, self.edited_form_data_author['text'])
        self.assertEqual(note.slug, self.edited_form_data_author['slug'])
        self.assertEqual(note.author, self.author_client)

    def test_edit_note_not_author(self):
        """
        Проверка страницы редактирования заметки.

            Проверяем, что пользователь не может редактировать чужие заметки.

                Порядок действий:
                    1. Делаем post запрос к чужой заметке с новыми данными.
                    2. Проверяем поля.

                Используемые методы:
                    1. assertEqual()
        """
        self.auth_author.post(
            self.url_edit_note_not_author,
            self.edited_form_data_not_author
        )
        note = Note.objects.get(pk=self.note_not_author.id)
        self.assertEqual(note.title, self.note_not_author.title)
        self.assertEqual(
            note.text, self.note_not_author.text
        )
        self.assertEqual(note.slug, self.note_not_author.slug)
        self.assertEqual(note.author, self.not_author)

    def test_delete_note_author(self):
        """
        Проверка страницы удаления заметки.

            Проверяем, что пользователь может удалять свои заметки,

            Порядок действий:
                    1. Считаем количество заметок.
                    2. Делаем delete запрос к своей заметке.
                    3. Снова считаем количество заметок,
                    4. Сравниваем количество заметок ДО и ПОСЛЕ delete запроса,
                        должно быть на 1 меньше.
                    5. Так же дополнительно проверяем что сработал редирект
                        после удаления.

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
            notes_count_after_post_request,
            notes_count_before_post_request - self.notes_difference_count
        )
        self.assertRedirects(response_from_author_note, self.success_url)

    def test_delete_note_not_author(self):
        """
        Проверка страницы удаления заметки.

            Проверяем, что пользователь не может удалять чужие заметки,

            Порядок действий:
                    1. Считаем количество заметок.
                    2. Делаем delete запрос к чужой заметке.

                Используемые методы:
                    1. assertRedirect()
                    2. assertEqual()
        """
        notes_count_before_post_request = Note.objects.count()
        response = self.auth_author.delete(
            self.url_delete_note_not_author
        )
        notes_count_after_post_request = Note.objects.count()
        self.assertEqual(
            notes_count_after_post_request, notes_count_before_post_request
        )
        self.assertEqual(
            response.status_code, HTTPStatus.NOT_FOUND
        )
