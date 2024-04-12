from django.contrib.auth import get_user_model
from django.urls import reverse

from .fixtures import AddFixture
from notes.forms import NoteForm

User = get_user_model()


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
        response = self.auth_author.get(self.list_page_url)
        notes = response.context['object_list']
        self.assertIn(self.note_author, notes)

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
        response = self.auth_author.get(self.list_page_url)
        notes = response.context['object_list']
        self.assertNotIn(self.note_not_author, notes)

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
