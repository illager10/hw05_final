from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from http import HTTPStatus
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description',
        )
        cls.private_urls = (
            (reverse('posts:post_edit', kwargs={'post_id': '1'}),
                'posts/create_post.html'),
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (reverse('posts:follow_index'), 'posts/follow.html'),
            (reverse('posts:profile', kwargs={'username': 'test_username'}),
                'posts/profile.html'),
        )
        cls.public_urls = (
            (reverse('posts:index'), 'posts/index.html'),
            (reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
                'posts/group_list.html'),
            (reverse('posts:post_detail', kwargs={'post_id': '1'}),
                'posts/post_detail.html'),
        )
        cls.user = User.objects.create_user(username='test_username')
        cls.post = Post.objects.create(
            text='test_text',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_correct_template_and_access_to_pages(self):
        """
        URL-адрес неавторизованного полтзователя
         использует соответствующий шаблон.
        Пользователь имеет доступ к странице.
        """
        for address, template in self.public_urls:
            with self.subTest(address=address, template=template):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_error_unexpected_page(self):
        """Несуществующая страница выдаёт ошибку, применяется шаблон ошибки"""
        response = self.guest_client.get('/unexpected_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_redirecting_guest_client(self):
        """
        Неавтоизованный пользователь перенаправляется на страницу регистрации
        """
        urls_tuple = (
            (reverse('posts:post_create'), '/auth/login/?next=/create/'),
            (reverse('posts:post_edit', kwargs={'post_id': '1'}),
                '/auth/login/?next=/posts/1/edit/')
        )
        for address, redirection in urls_tuple:
            with self.subTest(address=address, redirection=redirection):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, (redirection))

    def test_authorized_client_correct_template_and_access_to_pages(self):
        """
        URL-адрес авторизованного полтзователя
         использует соответствующий шаблон.
        Пользователь имеет доступ к странице.
        """
        for address, template in self.private_urls:
            with self.subTest(address=address, template=template):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
