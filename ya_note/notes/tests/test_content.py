from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class AddFixture(TestCase):

    LIST_PAGE_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создаем фикстуры для тестов."""
        cls.author = User.objects.create(username='test_user')
        cls.author_another_note = User.objects.create(
            username='test_user2'
        )
        cls.note_author = Note.objects.create(
            title='Заметка',
            text='Просто текст.',
            slug='test_slug',
            author=cls.author
        )
        cls.note_author_another_note = Note.objects.create(
            title='Заметка2',
            text='Просто текст2.',
            slug='test_slug2',
            author=cls.author_another_note
        )
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)


class TestListPage(AddFixture):

    def test_note_on_listpage(self):
        """
        Проверка отображения заметок.

            Проверяем, что созданная заметка отображается
            у автора в списке заметок.

                Порядок действий:
                    1. Получаем словарь context страницы list.
                    2. Проверяем, что созданная заметка находится в context.

                Используемые методы:
                    1. assertIn()
        """
        response = self.auth_author.get(self.LIST_PAGE_URL)
        note_list = response.context['object_list']
        self.assertIn(self.note_author, note_list)

    def test_list_only_for_author(self):
        """
        Проверка отображения заметок.

            Проверяем, что в списке заметок отображаются только
            заметки принадлежащие автору.

                Порядок действий:
                    1. Получаем словарь context страницы list.
                    2. Проверяем что заметка другого автора
                                    не находится в context.

                Используемые методы:
                    1. assertNotIn()
        """
        response = self.auth_author.get(self.LIST_PAGE_URL)
        note_list = response.context['object_list']
        self.assertNotIn(self.note_author_another_note, note_list)

    def test_form_in_add_delete_pages(self):
        """
        Проверка наличия формы.

            Проверяем, что отдельная форма передаётся
            на страницы создания и редактирования.

                Порядок действий:
                    1. Получаем одну из страниц.
                    2. Проверяем, есть ли form в словаре context.
                    3. Проверяем форму на соответствие необходимой.

                Используемые методы:
                    1. assertIn()
                    2. assertIsInstance()
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note_author.slug,))
        )
        for item in urls:
            path, args = item
            with self.subTest(path=path, args=args):
                url = reverse(path, args=args)
                response = self.auth_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'], NoteForm
                )
