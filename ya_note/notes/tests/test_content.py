from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.fixtures import AddFixture

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

    def test_form_in_add_edit_pages(self):
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
            (self.url_add),
            (self.url_edit_note_author)
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'], NoteForm
                )
