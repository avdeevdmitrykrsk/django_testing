from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):
    LIST_PAGE_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создаем фикстуры для тестов."""
        cls.author1 = User.objects.create(username='test_user')
        cls.author2 = User.objects.create(username='test_user2')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Просто текст.',
            slug='test_slug',
            author=cls.author1
        )
        cls.note2 = Note.objects.create(
            title='Заметка2',
            text='Просто текст2.',
            slug='test_slug2',
            author=cls.author2
        )

    def test_note_on_listpage(self):
        """
        Проверяем, что созданная заметка отображается
        у автора в списке заметок.
        """
        self.client.force_login(self.author1)
        response = self.client.get(self.LIST_PAGE_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_list_only_for_author(self):
        """
        Проверяем, что в списке заметок отображаются только
        заметки принадлежащие автору.
        """
        self.client.force_login(self.author1)
        response = self.client.get(self.LIST_PAGE_URL)
        list_objects = response.context['object_list']
        self.assertNotIn(self.note2, list_objects)

    def test_form_in_edit_delete_pages(self):
        """Проверяем, что отдельная заметка передаётся
        на страницу со списком заметок.
        """
        self.client.force_login(self.author1)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for item in urls:
            path, args = item
            with self.subTest():
                url = reverse(path, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'], NoteForm
                )
