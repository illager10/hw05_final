from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from ..models import Group, Post
from django.conf import settings
import tempfile
import shutil

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description',
        )
        cls.templates_pages_names = (
            (reverse('posts:index'), 'posts/index.html'),
            (reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
                'posts/group_list.html'),
            (reverse('posts:profile', kwargs={'username': 'test_usrneme'}),
                'posts/profile.html'),
            (reverse('posts:post_detail', kwargs={'post_id': '1'}),
                'posts/post_detail.html'),
            (reverse('posts:post_edit', kwargs={'post_id': '1'}),
                'posts/create_post.html'),
            (reverse('posts:post_create'), 'posts/create_post.html'),
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='test_usrneme')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='test_text',
            author=self.user,
            group=self.group,
            image=self.image,
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.fields.ChoiceField),
            ('image', forms.fields.ImageField),
        )
        self.assertTrue(isinstance(response.context.get('form'), PostForm))
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.fields.ChoiceField),
            ('image', forms.fields.ImageField),
        )
        self.assertTrue(isinstance(response.context.get('form'), PostForm))
        self.assertTrue(response.context.get('is_edit'))
        self.assertIsInstance(response.context.get('is_edit'), bool)
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_many_post_correct_context(self):
        """Шаблоны, содержащие множдество постов содржат правильный контекст"""
        templates_pages_names = (
            (reverse('posts:index'), 'page_obj'),
            (reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
             'page_obj'),
            (reverse('posts:profile', kwargs={'username': 'test_usrneme'}),
             'page_obj'),
            (reverse('posts:post_detail', kwargs={'post_id': '1'}), 'post')
        )
        for templates, object in templates_pages_names:
            with self.subTest(templates=templates, object=object):
                response = self.authorized_client.get(templates)
                if isinstance(response.context[object], Post):
                    first_object = response.context[object]
                else:
                    first_object = response.context[object][0]
                self.assertEqual(first_object.text, 'test_text')
                self.assertEqual(first_object.group, self.group)
                self.assertEqual(first_object.author, self.user)
                self.assertEqual(first_object.pub_date.date(),
                                 timezone.now().date())
                self.assertEqual(first_object.image, 'posts/small.gif')

    def test_pos_without_group_not_on_the_page(self):
        """
        Пост без группы не отображается на соответсвующих страницах
        """
        Group.objects.create(
            title='test_title',
            slug='group_without_posts',
            description='test_description',
        )
        Post.objects.create(
            text='test_without_groups',
            author=self.user,
        )

        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': 'group_without_posts'}))
                    )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_usrneme')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description',
        )
        cls.posts = [
            Post(
                text='test_text',
                author=cls.user,
                group=cls.group
            ) for i in range(11)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Тестируем пагинатор. На первой странице 10 постов"""
        URL_list = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'test_usrneme'}),
        )
        for reverse_name in URL_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), settings.PAGE_CONST
                )

    def test_second_page_contains_three_records(self):
        """Тестируем пагинатор. На второй странице 1 пост"""
        URL_list = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'test_usrneme'}),
        )
        for reverse_name in URL_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 1)
